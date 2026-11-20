"""Web search adapters and a safe page fetcher for AI Research (M01) and Fact Checker (M02).

Search providers (D-SEARCH): Tavily and Exa free tiers behind one interface, plus deterministic
fixtures for tests and the offline demo. The fetcher blocks SSRF: only public http(s) addresses,
limited size, time and redirects. Fetched pages are untrusted data for the model.
"""

import html
import ipaddress
import re
import socket
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urljoin, urlparse

import httpx

from app.core.config import get_settings
from app.core.errors import AppError


@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str
    published: str | None = None


class SearchProvider(Protocol):
    id: str
    name: str

    def configured(self) -> bool: ...

    def search(self, query: str, max_results: int = 5) -> list[SearchHit]: ...


class FixtureSearch:
    """Offline, deterministic results. Clearly labelled as demo data in the UI."""

    id, name = "fixture", "Offline demo sources"

    def configured(self) -> bool:
        return True

    def search(self, query: str, max_results: int = 5) -> list[SearchHit]:
        slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:40] or "topic"
        return [
            SearchHit(
                title=f"Demo source {i + 1} about {query[:60]}",
                url=f"https://example.org/{slug}/{i + 1}",
                snippet=f"Demo snippet {i + 1}: offline placeholder text about {query[:80]}.",
            )
            for i in range(min(max_results, 3))
        ]


class TavilySearch:
    id, name = "tavily", "Tavily"

    def _key(self) -> str | None:
        k = get_settings().tavily_api_key
        return k.get_secret_value() if k else None

    def configured(self) -> bool:
        return bool(self._key())

    def search(self, query: str, max_results: int = 5) -> list[SearchHit]:
        r = _post(
            "https://api.tavily.com/search",
            {"query": query, "max_results": max_results, "search_depth": "basic"},
            {"Authorization": f"Bearer {self._key()}"},
            self.name,
        )
        return [
            SearchHit(
                x.get("title", ""),
                x.get("url", ""),
                x.get("content", "")[:500],
                x.get("published_date"),
            )  # fmt: skip
            for x in r.get("results", [])
            if x.get("url")
        ]


class ExaSearch:
    id, name = "exa", "Exa"

    def _key(self) -> str | None:
        k = get_settings().exa_api_key
        return k.get_secret_value() if k else None

    def configured(self) -> bool:
        return bool(self._key())

    def search(self, query: str, max_results: int = 5) -> list[SearchHit]:
        r = _post(
            "https://api.exa.ai/search",
            {
                "query": query,
                "numResults": max_results,
                "contents": {"text": {"maxCharacters": 500}},
            },
            {"x-api-key": self._key() or ""},
            self.name,
        )
        return [
            SearchHit(
                x.get("title") or x.get("url", ""),
                x.get("url", ""),
                (x.get("text") or "")[:500],
                x.get("publishedDate"),
            )  # fmt: skip
            for x in r.get("results", [])
            if x.get("url")
        ]


def _post(url: str, body: dict[str, object], headers: dict[str, str], name: str) -> dict:  # type: ignore[type-arg]
    try:
        r = httpx.post(url, json=body, headers=headers, timeout=20)
    except httpx.HTTPError as e:
        raise AppError("search_unreachable", f"Could not reach {name}.", 502) from e
    if r.status_code == 429:
        raise AppError("search_quota", f"{name} free search limit reached.", 429)
    if r.status_code >= 400:
        raise AppError("search_error", f"{name} returned an error ({r.status_code}).", 502)
    data = r.json()
    return data if isinstance(data, dict) else {}


SEARCH_PROVIDERS: dict[str, SearchProvider] = {
    p.id: p for p in (TavilySearch(), ExaSearch(), FixtureSearch())
}


def default_search() -> SearchProvider:
    for pid in ("tavily", "exa"):
        if SEARCH_PROVIDERS[pid].configured():
            return SEARCH_PROVIDERS[pid]
    return SEARCH_PROVIDERS["fixture"]


# ---------------- safe fetching ----------------

MAX_BYTES = 2_000_000
MAX_REDIRECTS = 3


def is_public_address(host: str) -> bool:
    """Resolve and reject loopback, private, link-local, metadata and other non-public ranges."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global or ip.is_multicast:
            return False
    return bool(infos)


def check_url(url: str) -> str:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise AppError("blocked_url", "Only public http(s) links can be fetched.", 400)
    if p.username or p.password:
        raise AppError("blocked_url", "Links with embedded credentials are not allowed.", 400)
    if not is_public_address(p.hostname):
        raise AppError("blocked_url", "This address is not publicly reachable.", 400)
    return url


def fetch_text(url: str) -> tuple[str, str]:
    """Fetch a public page and return (final_url, plain text). Redirect targets are re-checked."""
    current = check_url(url)
    with httpx.Client(timeout=15, follow_redirects=False,
                      headers={"User-Agent": "AURA-Research/0.1"}) as client:  # fmt: skip
        for _ in range(MAX_REDIRECTS + 1):
            with client.stream("GET", current) as r:
                if r.is_redirect and "location" in r.headers:
                    current = check_url(urljoin(current, r.headers["location"]))
                    continue
                if r.status_code >= 400:
                    raise AppError("fetch_failed", f"The page returned {r.status_code}.", 502)
                ctype = r.headers.get("content-type", "")
                if "html" not in ctype and "text" not in ctype:
                    raise AppError("unsupported_content", "Only web pages can be read.", 415)
                buf = bytearray()
                for chunk in r.iter_bytes():
                    buf.extend(chunk)
                    if len(buf) > MAX_BYTES:
                        break
                return current, html_to_text(buf.decode(r.encoding or "utf-8", "replace"))
    raise AppError("fetch_failed", "Too many redirects.", 502)


_DROP = re.compile(r"(?is)<(script|style|noscript|svg|nav|footer|header|form)[^>]*>.*?</\1>")
_TAGS = re.compile(r"(?s)<[^>]+>")
_WS = re.compile(r"[ \t\r\f\v]+")


def html_to_text(doc: str) -> str:
    """Dependency-free main-text extraction; good enough for citations (trafilatura if needed)."""
    text = _DROP.sub(" ", doc)
    text = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6])[^>]*>", "\n", text)
    text = html.unescape(_TAGS.sub(" ", text))
    lines = [_WS.sub(" ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if len(line) > 1)[:50_000]
