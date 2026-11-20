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
    served_by: str = ""  # "provider/model" that actually answered (set by AutoProvider)


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
    account_setting: str | None = None  # e.g. Cloudflare account id, filled into "{account}"
    in_auto: bool = True  # False for non-production free tiers (kept out of Auto failover)

    def _key(self) -> str | None:
        v = getattr(get_settings(), self.api_key_setting, None)
        return v.get_secret_value() if v else None

    def _url(self) -> str:
        acct = getattr(get_settings(), self.account_setting, None) if self.account_setting else ""
        return self.base_url.replace("{account}", acct or "")

    def configured(self) -> bool:
        acct_ok = not self.account_setting or bool(getattr(get_settings(), self.account_setting))
        return bool(self._key()) and acct_ok

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
                f"{self._url()}/chat/completions",
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


def _compat(
    pid: str,
    name: str,
    url: str,
    key: str,
    model: str,
    label: str,
    ctx: int,
    note: str,
    policy: str,
    **kw: object,
) -> OpenAICompatibleProvider:
    info = ProviderInfo(pid, name, False, note, policy, (ModelInfo(model, label, ctx),))
    return OpenAICompatibleProvider(info, url, key, **kw)  # type: ignore[arg-type]


# Additional free tiers (2026-11-20). Confirm model ids in each console when adding keys.
PROVIDERS.update(
    {
        "mistral": _compat(
            "mistral",
            "Mistral (free Experiment plan)",
            "https://api.mistral.ai/v1",
            "mistral_api_key",
            "mistral-small-latest",
            "Mistral Small",
            128_000,
            "Free plan with per-model monthly limits; phone verification at sign-up.",
            "Free-plan API data may be used for training unless you opt out in the admin console.",
        ),
        "cloudflare": _compat(
            "cloudflare",
            "Cloudflare Workers AI",
            "https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1",
            "cloudflare_api_token",
            "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
            "Llama 3.3 70B",
            24_000,
            "10,000 Neurons per day free; requests fail after that until 00:00 UTC.",
            "Cloudflare states it does not train on customer content.",
            account_setting="cloudflare_account_id",
        ),
        "cerebras": _compat(
            "cerebras",
            "Cerebras (free trial)",
            "https://api.cerebras.ai/v1",
            "cerebras_api_key",
            "gpt-oss-120b",
            "GPT-OSS 120B",
            131_072,
            "Trial only: $5 of credit that expires after 30 days.",
            "See Cerebras terms (not yet verified by AURA).",
        ),
        "huggingface": _compat(
            "huggingface",
            "Hugging Face Inference",
            "https://router.huggingface.co/v1",
            "huggingface_api_key",
            "openai/gpt-oss-20b",
            "GPT-OSS 20B",
            131_072,
            "Very small free monthly credit (about $0.10).",
            "Routed to third-party inference providers; policies vary.",
        ),
        "nvidia": _compat(
            "nvidia",
            "NVIDIA NIM (development only)",
            "https://integrate.api.nvidia.com/v1",
            "nvidia_api_key",
            "openai/gpt-oss-120b",
            "GPT-OSS 120B",
            131_072,
            "Free for prototyping and testing only; not allowed for production use.",
            "Developer Program terms: non-production use only.",
            in_auto=False,
        ),
    }
)
AUTO_ORDER = ["groq", "gemini", "cerebras", "mistral", "cloudflare", "openrouter", "huggingface"]

FAILOVER_CODES = {
    "provider_quota",
    "provider_error",
    "provider_timeout",
    "provider_unreachable",
    "provider_unconfigured",
}
LONG_CONTEXT_TOKENS = 100_000


class AutoProvider:
    """Picks a free provider per request and fails over to the next one on limits or errors.

    Order: Groq (fast) -> Gemini (largest context) -> OpenRouter free; very long inputs try Gemini
    first. Only free, configured providers are candidates: it never falls back to a paid provider,
    and it never silently falls back to the offline demo model.
    """

    info = ProviderInfo(
        id="auto",
        name="Auto (best free model)",
        paid=False,
        free_tier_note="Chooses a free provider per request and switches if one hits its limit.",
        data_policy="Messages go to whichever free provider answers; see each provider's policy.",
        models=(ModelInfo("auto", "Auto", 1_000_000),),
    )

    def candidates(self, input_tokens: int) -> list[str]:
        order = list(AUTO_ORDER)
        if input_tokens > LONG_CONTEXT_TOKENS:
            order = ["gemini", *[p for p in order if p != "gemini"]]
        return [
            p
            for p in order
            if PROVIDERS[p].configured()
            and not PROVIDERS[p].info.paid
            and getattr(PROVIDERS[p], "in_auto", True)
        ]

    def configured(self) -> bool:
        return bool(self.candidates(0))

    def stream(
        self, model: str, messages: list[ChatMessage], result: StreamResult
    ) -> Iterator[str]:
        tokens = sum(estimate_tokens(m.content) for m in messages)
        last: AppError | None = None
        for pid in self.candidates(tokens):
            p = PROVIDERS[pid]
            m = max(p.info.models, key=lambda x: x.context_window)
            if m.context_window < tokens:
                continue
            started = False
            try:
                for chunk in p.stream(m.id, messages, result):
                    started = True
                    yield chunk
                result.served_by = f"{pid}/{m.id}"
                return
            except AppError as e:
                if started or e.code not in FAILOVER_CODES:
                    raise  # never splice two providers' answers together
                last = e
        raise AppError(
            "no_free_provider",
            "No free model is available right now. Please try again later.",
            last.status if last else 503,
        )


PROVIDERS["auto"] = AutoProvider()


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
