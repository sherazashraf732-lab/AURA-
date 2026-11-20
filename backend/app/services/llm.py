"""One-shot model call shared by Coding Lab, Workflows and other single-prompt features."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.chat import UsageEvent
from app.modules.providers import ChatMessage, StreamResult, get_provider, model_info


def complete(
    db: Session, user_id: UUID, kind: str, provider_id: str, model: str, system: str, user: str
) -> tuple[str, str]:
    """Returns (text, served_by). Callers must run chat.ensure_provider_usable first."""
    provider = get_provider(provider_id)
    model_info(provider, model)
    result = StreamResult()
    msgs = [ChatMessage("system", system), ChatMessage("user", user)]
    text = "".join(provider.stream(model, msgs, result))
    db.add(
        UsageEvent(
            user_id=user_id,
            kind=kind,
            provider=provider_id,
            model=model,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            latency_ms=result.latency_ms,
        )
    )
    return text, result.served_by or f"{provider_id}/{model}"
