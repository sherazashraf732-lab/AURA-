import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, or_, select

from app.api.deps import CurrentUser, DbSession, VerifiedUser
from app.core.config import get_settings
from app.core.errors import AppError
from app.database.session import utcnow
from app.models.chat import Conversation, ConversationSummary, Message, UserMemory
from app.modules.providers import PROVIDERS, get_provider, model_info
from app.services import chat as svc

router = APIRouter(tags=["chat"])

# ---------------- providers & usage ----------------


@router.get("/models")
def list_models(user: CurrentUser) -> list[dict[str, object]]:
    s = get_settings()
    return [
        {
            "id": p.info.id,
            "name": p.info.name,
            "paid": p.info.paid,
            "available": p.configured() and (not p.info.paid or s.allow_paid_provider_usage),
            "requires_consent": p.info.requires_consent,
            "free_tier_note": p.info.free_tier_note,
            "data_policy": p.info.data_policy,
            "models": [
                {"id": m.id, "label": m.label, "context_window": m.context_window}
                for m in p.info.models
            ],
        }
        for p in PROVIDERS.values()
    ]


@router.get("/usage/me")
def my_usage(user: CurrentUser, db: DbSession) -> dict[str, object]:
    s = get_settings()
    return {
        "today": svc.usage_today(db, user),
        "daily_limit_per_provider": s.default_user_daily_request_limit,
        "demo_daily_limit": s.default_user_daily_request_limit * svc.MOCK_DAILY_MULTIPLIER,
        "paid_usage_enabled": s.allow_paid_provider_usage,
    }


# ---------------- conversations ----------------


class ConversationIn(BaseModel):
    provider: str = "mock"
    model: str = "aura-mock-1"
    project_id: UUID | None = None
    title: str | None = Field(default=None, max_length=200)


class ConversationPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    archived: bool | None = None
    provider: str | None = None
    model: str | None = None
    language_override: str | None = Field(default=None, pattern=r"^(auto|en|ur|ur-Latn)$")


class ConversationOut(BaseModel):
    id: UUID
    title: str
    provider: str
    model: str
    project_id: UUID | None
    archived: bool
    continued_from_id: UUID | None
    continuation_summary_id: UUID | None
    language_override: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def of(cls, c: Conversation) -> "ConversationOut":
        return cls(
            id=c.id,
            title=c.title,
            provider=c.provider,
            model=c.model,
            project_id=c.project_id,
            archived=c.archived_at is not None,
            continued_from_id=c.continued_from_id,
            continuation_summary_id=c.continuation_summary_id,
            language_override=c.language_override,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )


class MessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    language: str | None
    provider: str | None
    model: str | None
    status: str
    error_code: str | None
    created_at: datetime


def _validate_model(provider: str, model: str) -> None:
    model_info(get_provider(provider), model)


@router.post("/conversations", status_code=201)
def create_conversation(body: ConversationIn, user: VerifiedUser, db: DbSession) -> ConversationOut:
    _validate_model(body.provider, body.model)
    if body.project_id:
        svc.get_project(db, user, body.project_id)
    c = Conversation(
        owner_id=user.id,
        provider=body.provider,
        model=body.model,
        project_id=body.project_id,
        title=body.title or "New chat",
    )
    db.add(c)
    db.flush()
    return ConversationOut.of(c)


@router.get("/conversations")
def list_conversations(
    user: CurrentUser,
    db: DbSession,
    q: str | None = Query(default=None, max_length=200),
    archived: bool = False,
    project_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ConversationOut]:
    stmt = select(Conversation).where(Conversation.owner_id == user.id)
    stmt = stmt.where(
        Conversation.archived_at.is_not(None) if archived else Conversation.archived_at.is_(None)
    )
    if project_id:
        stmt = stmt.where(Conversation.project_id == project_id)
    if q:
        escaped = q.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
        like = f"%{escaped}%"
        matching = select(Message.conversation_id).where(
            Message.owner_id == user.id, Message.content.ilike(like, escape="\\")
        )
        stmt = stmt.where(
            or_(Conversation.title.ilike(like, escape="\\"), Conversation.id.in_(matching))
        )
    rows = db.scalars(stmt.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset))
    return [ConversationOut.of(c) for c in rows]


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: UUID, user: CurrentUser, db: DbSession) -> ConversationOut:
    return ConversationOut.of(svc.get_conversation(db, user, conversation_id))


@router.patch("/conversations/{conversation_id}")
def update_conversation(
    conversation_id: UUID, body: ConversationPatch, user: CurrentUser, db: DbSession
) -> ConversationOut:
    c = svc.get_conversation(db, user, conversation_id)
    if body.title is not None:
        c.title = body.title.strip()
    if body.archived is not None:
        c.archived_at = utcnow() if body.archived else None
    if body.provider is not None or body.model is not None:
        provider, model = body.provider or c.provider, body.model or c.model
        _validate_model(provider, model)
        c.provider, c.model = provider, model
    if body.language_override is not None:
        c.language_override = None if body.language_override == "auto" else body.language_override
    return ConversationOut.of(c)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: UUID, user: CurrentUser, db: DbSession) -> None:
    c = svc.get_conversation(db, user, conversation_id)
    db.delete(c)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: UUID, user: CurrentUser, db: DbSession) -> list[MessageOut]:
    c = svc.get_conversation(db, user, conversation_id)
    rows = db.scalars(
        select(Message).where(Message.conversation_id == c.id).order_by(Message.created_at)
    )
    return [MessageOut.model_validate(m, from_attributes=True) for m in rows]


class SendIn(BaseModel):
    content: str = Field(min_length=1, max_length=20000)


@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: UUID, body: SendIn, user: VerifiedUser, db: DbSession
) -> StreamingResponse:
    conv = svc.get_conversation(db, user, conversation_id)
    if conv.archived_at is not None:
        raise AppError("archived", "Unarchive this chat to continue it.", 409)
    svc.prepare_send(db, user, conv)
    return StreamingResponse(
        svc.stream_reply(user.id, conv.id, body.content),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/conversations/{conversation_id}/continue", status_code=201)
def continue_conversation(
    conversation_id: UUID, user: VerifiedUser, db: DbSession
) -> ConversationOut:
    conv = svc.get_conversation(db, user, conversation_id)
    svc.prepare_send(db, user, conv)
    return ConversationOut.of(svc.continue_conversation(db, user, conv))


@router.get("/conversations/{conversation_id}/export")
def export_conversation(
    conversation_id: UUID, user: CurrentUser, db: DbSession
) -> dict[str, object]:
    c = svc.get_conversation(db, user, conversation_id)
    return {
        "conversation": ConversationOut.of(c).model_dump(mode="json"),
        "messages": [
            MessageOut.model_validate(m, from_attributes=True).model_dump(mode="json")
            for m in db.scalars(
                select(Message).where(Message.conversation_id == c.id).order_by(Message.created_at)
            )
        ],
    }


# ---------------- summaries ----------------


class SummaryOut(BaseModel):
    id: UUID
    conversation_id: UUID
    version: int
    content: dict[str, object]
    provider: str
    model: str
    created_at: datetime


@router.get("/summaries")
def list_summaries(user: CurrentUser, db: DbSession) -> list[SummaryOut]:
    rows = db.scalars(
        select(ConversationSummary)
        .where(ConversationSummary.owner_id == user.id)
        .order_by(ConversationSummary.created_at.desc())
        .limit(100)
    )
    return [SummaryOut.model_validate(s, from_attributes=True) for s in rows]


def _summary(db: DbSession, user: CurrentUser, summary_id: UUID) -> ConversationSummary:
    s = db.scalar(
        select(ConversationSummary).where(
            ConversationSummary.id == summary_id, ConversationSummary.owner_id == user.id
        )
    )
    if s is None:
        raise AppError("not_found", "Summary not found.", 404)
    return s


@router.get("/summaries/{summary_id}")
def get_summary(summary_id: UUID, user: CurrentUser, db: DbSession) -> SummaryOut:
    return SummaryOut.model_validate(_summary(db, user, summary_id), from_attributes=True)


class SummaryPatch(BaseModel):
    content: dict[str, object]


@router.put("/summaries/{summary_id}")
def edit_summary(
    summary_id: UUID, body: SummaryPatch, user: CurrentUser, db: DbSession
) -> SummaryOut:
    s = _summary(db, user, summary_id)
    s.content = svc.parse_summary(json.dumps(body.content))
    return SummaryOut.model_validate(s, from_attributes=True)


@router.delete("/summaries/{summary_id}", status_code=204)
def delete_summary(summary_id: UUID, user: CurrentUser, db: DbSession) -> None:
    db.delete(_summary(db, user, summary_id))


# ---------------- durable memory ----------------


class MemoryIn(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    project_id: UUID | None = None


class MemoryPatch(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=500)
    enabled: bool | None = None


class MemoryOut(BaseModel):
    id: UUID
    content: str
    project_id: UUID | None
    source: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


MAX_MEMORIES = 200


@router.get("/memory")
def list_memory(
    user: CurrentUser, db: DbSession, project_id: UUID | None = None
) -> list[MemoryOut]:
    stmt = select(UserMemory).where(UserMemory.owner_id == user.id)
    if project_id:
        stmt = stmt.where(UserMemory.project_id == project_id)
    rows = db.scalars(stmt.order_by(UserMemory.updated_at.desc()))
    return [MemoryOut.model_validate(m, from_attributes=True) for m in rows]


@router.post("/memory", status_code=201)
def create_memory(body: MemoryIn, user: CurrentUser, db: DbSession) -> MemoryOut:
    if body.project_id:
        svc.get_project(db, user, body.project_id)
    count = db.scalar(select(func.count(UserMemory.id)).where(UserMemory.owner_id == user.id))
    if (count or 0) >= MAX_MEMORIES:
        raise AppError("memory_full", f"You can keep up to {MAX_MEMORIES} memories.", 409)
    m = UserMemory(owner_id=user.id, project_id=body.project_id, content=body.content.strip())
    db.add(m)
    db.flush()
    return MemoryOut.model_validate(m, from_attributes=True)


def _memory(db: DbSession, user: CurrentUser, memory_id: UUID) -> UserMemory:
    m = db.scalar(
        select(UserMemory).where(UserMemory.id == memory_id, UserMemory.owner_id == user.id)
    )
    if m is None:
        raise AppError("not_found", "Memory not found.", 404)
    return m


@router.patch("/memory/{memory_id}")
def update_memory(
    memory_id: UUID, body: MemoryPatch, user: CurrentUser, db: DbSession
) -> MemoryOut:
    m = _memory(db, user, memory_id)
    if body.content is not None:
        m.content = body.content.strip()
    if body.enabled is not None:
        m.enabled = body.enabled
    m.updated_at = utcnow()
    return MemoryOut.model_validate(m, from_attributes=True)


@router.delete("/memory/{memory_id}", status_code=204)
def delete_memory(memory_id: UUID, user: CurrentUser, db: DbSession) -> None:
    db.delete(_memory(db, user, memory_id))


@router.delete("/memory", status_code=204)
def delete_all_memory(user: CurrentUser, db: DbSession) -> None:
    db.execute(delete(UserMemory).where(UserMemory.owner_id == user.id))
