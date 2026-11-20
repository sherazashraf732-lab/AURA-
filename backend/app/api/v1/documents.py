import re

from fastapi import APIRouter, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.api.deps import DbSession, VerifiedUser
from app.core.ratelimit import enforce
from app.models.chat import UsageEvent
from app.modules import language
from app.modules.providers import ChatMessage, StreamResult, get_provider, model_info
from app.services import chat as chat_svc
from app.services import documents as svc

router = APIRouter(prefix="/documents", tags=["documents"])


class RenderIn(BaseModel):
    format: svc.Format
    content: svc.DocContent


@router.post("/render")
def render(body: RenderIn, request: Request, user: VerifiedUser) -> Response:
    enforce(request, "render", limit=60, window_s=3600, key=str(user.id))
    data = svc.render(body.format, body.content)
    name = re.sub(r"[^\w\- ]+", "", body.content.title).strip()[:80] or "document"
    return Response(
        data,
        media_type=svc.MIME[body.format],
        headers={"Content-Disposition": f'attachment; filename="{name}.{body.format}"'},
    )


class DraftIn(BaseModel):
    prompt: str = Field(min_length=3, max_length=4000)
    provider: str = "mock"
    model: str = "aura-mock-1"


@router.post("/draft")
def draft(body: DraftIn, user: VerifiedUser, db: DbSession) -> svc.DocContent:
    chat_svc.ensure_provider_usable(db, user, body.provider)
    provider = get_provider(body.provider)
    model_info(provider, body.model)
    lang = language.resolve(body.prompt, user.language_override, None).reply_instruction()
    result = StreamResult()
    msgs = [ChatMessage("system", svc.DRAFT_PROMPT.replace("{language}", lang)),
            ChatMessage("user", body.prompt)]  # fmt: skip
    raw = "".join(provider.stream(body.model, msgs, result))
    db.add(UsageEvent(user_id=user.id, kind="document", provider=body.provider, model=body.model,
                      tokens_in=result.tokens_in, tokens_out=result.tokens_out,
                      latency_ms=result.latency_ms))  # fmt: skip
    return svc.parse_draft(raw, body.prompt.splitlines()[0])
