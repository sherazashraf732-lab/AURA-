"""Security Center (M19): sessions, audit history, data export and account deletion."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import Select, select, update

from app.api.deps import SESSION_COOKIE, CurrentUser, DbSession
from app.core.errors import AppError
from app.core.ratelimit import enforce
from app.core.security import hash_token, verify_password
from app.database.session import utcnow
from app.models.chat import Conversation, ConversationSummary, Message, UserMemory
from app.models.data import Dataset
from app.models.identity import AuditEvent, AuthSession, Project
from app.models.knowledge import DocumentChunk, KnowledgeSource
from app.models.workflows import Workflow
from app.services.auth import audit

router = APIRouter(prefix="/security", tags=["security"])


class SessionOut(BaseModel):
    id: UUID
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    user_agent: str | None
    current: bool


@router.get("/sessions")
def sessions(request: Request, user: CurrentUser, db: DbSession) -> list[SessionOut]:
    mine = hash_token(request.cookies.get(SESSION_COOKIE, ""))
    rows = db.scalars(
        select(AuthSession)
        .where(
            AuthSession.user_id == user.id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > utcnow(),
        )
        .order_by(AuthSession.last_seen_at.desc())
    )
    return [
        SessionOut(
            id=s.id,
            created_at=s.created_at,
            last_seen_at=s.last_seen_at,
            expires_at=s.expires_at,
            user_agent=s.user_agent,
            current=s.token_hash == mine,
        )
        for s in rows
    ]


@router.post("/sessions/revoke-others", status_code=204)
def revoke_others(request: Request, user: CurrentUser, db: DbSession) -> None:
    mine = hash_token(request.cookies.get(SESSION_COOKIE, ""))
    db.execute(
        update(AuthSession)
        .where(
            AuthSession.user_id == user.id,
            AuthSession.token_hash != mine,
            AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=utcnow())
    )
    audit(db, "user.revoke_other_sessions", user)


@router.delete("/sessions/{session_id}", status_code=204)
def revoke(session_id: UUID, user: CurrentUser, db: DbSession) -> None:
    s = db.scalar(
        select(AuthSession).where(AuthSession.id == session_id, AuthSession.user_id == user.id)
    )
    if s is None:
        raise AppError("not_found", "Session not found.", 404)
    s.revoked_at = utcnow()


@router.get("/audit")
def audit_log(user: CurrentUser, db: DbSession) -> list[dict[str, object]]:
    rows = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.actor_id == user.id)
        .order_by(AuditEvent.created_at.desc())
        .limit(100)
    )
    return [{"at": e.created_at.isoformat(), "action": e.action, "detail": e.detail} for e in rows]


def _rows(db: DbSession, model: type, owner_col: str, uid: UUID, fields: list[str]) -> list[dict]:  # type: ignore[type-arg]
    q: Select[tuple[object]] = select(model).where(getattr(model, owner_col) == uid)
    return [{f: _j(getattr(r, f)) for f in fields} for r in db.scalars(q)]


def _j(v: object) -> object:
    return v.isoformat() if isinstance(v, datetime) else str(v) if isinstance(v, UUID) else v


@router.get("/export")
def export(request: Request, user: CurrentUser, db: DbSession) -> Response:
    """Everything AURA stores about the user, as one JSON download."""
    enforce(request, "export", limit=5, window_s=3600, key=str(user.id))
    import json

    uid = user.id
    data = {
        "exported_at": utcnow().isoformat(),
        "account": {
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
            "language_override": user.language_override,
            "memory_enabled": user.memory_enabled,
        },
        "projects": _rows(
            db, Project, "owner_id", uid, ["id", "name", "description", "instructions"]
        ),
        "conversations": _rows(
            db, Conversation, "owner_id", uid, ["id", "title", "provider", "model", "created_at"]
        ),
        "messages": _rows(
            db, Message, "owner_id", uid, ["conversation_id", "role", "content", "created_at"]
        ),
        "memories": _rows(
            db, UserMemory, "owner_id", uid, ["id", "content", "project_id", "enabled"]
        ),
        "summaries": _rows(
            db, ConversationSummary, "owner_id", uid, ["conversation_id", "version", "content"]
        ),
        "documents": _rows(
            db, KnowledgeSource, "owner_id", uid, ["id", "filename", "kind", "created_at"]
        ),
        "document_text": _rows(db, DocumentChunk, "owner_id", uid, ["source_id", "seq", "text"]),
        "datasets": _rows(db, Dataset, "owner_id", uid, ["id", "name", "columns", "rows"]),
        "workflows": _rows(db, Workflow, "owner_id", uid, ["id", "name", "version", "steps"]),
    }
    audit(db, "user.data_export", user)
    return Response(
        json.dumps(data, ensure_ascii=False, indent=1),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="aura-export.json"'},
    )


class DeleteIn(BaseModel):
    password: str = Field(min_length=1, max_length=256)
    confirm: str = Field(pattern=r"^DELETE$")


@router.post("/delete-account", status_code=204)
def delete_account(
    body: DeleteIn, request: Request, response: Response, user: CurrentUser, db: DbSession
) -> None:
    """Permanently deletes the account; every owned row is removed by ON DELETE CASCADE."""
    enforce(request, "delete-account", limit=5, window_s=3600, key=str(user.id))
    if not verify_password(user.password_hash, body.password):
        raise AppError("invalid_credentials", "Password is incorrect.", 401)
    db.add(AuditEvent(actor_id=None, action="user.deleted", target=str(user.id)))
    db.delete(user)
    response.delete_cookie(SESSION_COOKIE, path="/")
