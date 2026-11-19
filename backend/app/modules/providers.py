"""Provider-neutral model adapters (ADR-003).

Gemini, Groq, OpenRouter and Cloudflare all expose OpenAI-compatible chat endpoints, so one small
httpx adapter covers every free-tier provider without adding LiteLLM's heavy dependency tree.
Decision D-022: LiteLLM is deferred until a provider without an OpenAI-compatible API is enabled.
"""

import json
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Protocol

import httpx

from app.core.config import get_settings
from app.core.errors import AppError


@dataclass(frozen=True)
class ChatMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class StreamResult:
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0


@dataclass(frozen=True)
class ModelInfo:
    id: str
    label: str
    context_window: int


@dataclass(frozen=True)
class ProviderInfo:
    id: str
    name: str
    paid: bool
    free_tier_note: str
    data_policy: str
    models: tuple[ModelInfo, ...]
    requires_consent: bool = True


class Provider(Protocol):
    info: ProviderInfo

    def configured(self) -> bool: ...

    def stream(
        self, model: str, messages: list[ChatMessage], result: StreamResult
    ) -> Iterator[str]: ...


def estimate_tokens(text: str) -> int:
    """Cheap provider-agnostic estimate (~4 chars/token; Urdu script ~2) for quotas and context."""
    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    return max(1, (len(text) - non_ascii) // 4 + non_ascii // 2)


class MockProvider:
    """Deterministic offline provider for tests and demos. Always labelled as a demo in the UI."""

    info = ProviderInfo(
        id="mock",
        name="AURA Demo (offline)",
        paid=False,
        free_tier_note="Runs locally, no external calls. Replies are canned, not real AI.",
        data_policy="Nothing leaves the AURA server.",
        models=(ModelInfo("aura-mock-1", "Demo model", 8000),),
        requires_consent=False,
    )

    def configured(self) -> bool:
        return True

    def stream(
        self, model: str, messages: list[ChatMessage], result: StreamResult
    ) -> Iterator[str]:
        start = time.monotonic()
        last = next((m.content for m in reversed(messages) if m.role == "user"), "")
        system = "\n".join(m.content for m in messages if m.role == "system")
        if "SUMMARY_JSON" in system:
            reply = json.dumps(
                {
                    "goal": last[:200],
                    "key_facts": [],
                    "decisions": [],
                    "instructions": [],
                    "completed": [],
                    "pending": [],
                    "artifacts": [],
                    "open_questions": [],
                }
            )
        elif "Roman Urdu" in system:
            reply = f"(Demo jawab) Aap ne likha: {last[:300]}"
        elif "Urdu (Arabic) script" in system:
            reply = f"(ڈیمو جواب) آپ نے لکھا: {last[:300]}"
        else:
            reply = f"(Demo reply) You wrote: {last[:300]}"
        result.tokens_in = sum(estimate_tokens(m.content) for m in messages)
        for word in reply.split(" "):
            yield word + " "
        result.tokens_out = estimate_tokens(reply)
        result.latency_ms = int((time.monotonic() - start) * 1000)


@dataclass
class OpenAICompatibleProvider:
    info: ProviderInfo
    base_url: str
    api_key_setting: str
    extra_headers: dict[str, str] = field(default_factory=dict)

    def _key(self) -> str | None:
        v = getattr(get_settings(), self.api_key_setting, None)
        return v.get_secret_value() if v else None

    def configured(self) -> bool:
        return bool(self._key())

    def stream(
        self, model: str, messages: list[ChatMessage], result: StreamResult
    ) -> Iterator[str]:
        key = self._key()
        if not key:
            raise AppError("provider_unconfigured", f"{self.info.name} is not configured.", 503)
        start = time.monotonic()
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        headers = {"Authorization": f"Bearer {key}", **self.extra_headers}
        out_chars: list[str] = []
        try:
            with httpx.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=httpx.Timeout(60, connect=10),
            ) as r:
                if r.status_code == 429:
                    raise AppError(
                        "provider_quota", f"{self.info.name} free-tier limit reached.", 429
                    )
                if r.status_code >= 400:
                    raise AppError(
                        "provider_error",
                        f"{self.info.name} returned an error ({r.status_code}).",
                        502,
                    )
                for line in r.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    usage = chunk.get("usage")
                    if usage:
                        result.tokens_in = int(usage.get("prompt_tokens") or 0)
                        result.tokens_out = int(usage.get("completion_tokens") or 0)
                    for choice in chunk.get("choices") or []:
                        text = (choice.get("delta") or {}).get("content")
                        if text:
                            out_chars.append(text)
                            yield text
        except httpx.TimeoutException as e:
            raise AppError("provider_timeout", f"{self.info.name} timed out.", 504) from e
        except httpx.HTTPError as e:
            raise AppError("provider_unreachable", f"Could not reach {self.info.name}.", 502) from e
        if not result.tokens_in:
            result.tokens_in = sum(estimate_tokens(m.content) for m in messages)
        if not result.tokens_out:
            result.tokens_out = estimate_tokens("".join(out_chars))
        result.latency_ms = int((time.monotonic() - start) * 1000)


# Free-tier facts verified 2026-11-20 (PHASE_1_FREE_TIER_VERIFICATION.md). Model ids must be checked
# against each provider's live model list when keys are added; they change frequently.
PROVIDERS: dict[str, Provider] = {
    "mock": MockProvider(),
    "groq": OpenAICompatibleProvider(
        ProviderInfo(
            id="groq",
            name="Groq",
            paid=False,
            free_tier_note="Free tier; per-model daily request limits shared by all AURA users.",
            data_policy="See Groq's terms; free-tier data policy not yet verified by AURA.",
            models=(ModelInfo("openai/gpt-oss-120b", "GPT-OSS 120B", 131072),),
        ),
        "https://api.groq.com/openai/v1",
        "groq_api_key",
    ),
    "gemini": OpenAICompatibleProvider(
        ProviderInfo(
            id="gemini",
            name="Google Gemini (free tier)",
            paid=False,
            free_tier_note="Free tier with per-model limits shared by all AURA users.",
            data_policy=(
                "Google may use free-tier prompts and replies to improve its products and human "
                "reviewers may read them. Do not send personal or sensitive information. Not "
                "available to users in the EEA, UK or Switzerland."
            ),
            models=(ModelInfo("gemini-flash-latest", "Gemini Flash", 1_000_000),),
        ),
        "https://generativelanguage.googleapis.com/v1beta/openai",
        "gemini_api_key",
    ),
    "openrouter": OpenAICompatibleProvider(
        ProviderInfo(
            id="openrouter",
            name="OpenRouter (free models)",
            paid=False,
            free_tier_note="Free models: 20 requests/minute and 50 requests/day in total.",
            data_policy="Each free model's host has its own data policy; some may log prompts.",
            models=(ModelInfo("openai/gpt-oss-20b:free", "GPT-OSS 20B (free)", 131072),),
        ),
        "https://openrouter.ai/api/v1",
        "openrouter_api_key",
        {"X-Title": "AURA"},
    ),
}


def get_provider(provider_id: str) -> Provider:
    p = PROVIDERS.get(provider_id)
    if p is None:
        raise AppError("unknown_provider", "Unknown model provider.", 400)
    if p.info.paid and not get_settings().allow_paid_provider_usage:
        raise AppError("paid_disabled", "Paid providers are disabled.", 403)
    return p


def model_info(provider: Provider, model: str) -> ModelInfo:
    for m in provider.info.models:
        if m.id == model:
            return m
    raise AppError("unknown_model", "Unknown model for this provider.", 400)
