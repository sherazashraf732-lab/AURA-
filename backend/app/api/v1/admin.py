"""Admin Dashboard (M17): users, moderation, usage, provider status and audit events.

Every route requires a verified admin (AdminUser). Admin actions are audit-logged.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select, update

from app.api.deps import AdminUser, DbSession
from app.core.config import get_settings
from app.core.errors import AppError
from app.database.session import utcnow
from app.models.agents import AgentRun
from app.models.chat import UsageEvent
from app.models.identity import AuditEvent, AuthSession, User
from app.modules.providers import PROVIDERS
from app.services.auth import audit

router = APIRouter(prefix="/admin", tags=["admin"])


def _today() -> datetime:
    return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


@router.get("/stats")
def stats(admin: AdminUser, db: DbSession) -> dict[str, object]:
    since = _today()
    usage = db.execute(
        select(
            UsageEvent.provider,
            func.count(UsageEvent.id),
            func.sum(UsageEvent.tokens_in),
            func.sum(UsageEvent.tokens_out),
        )
        .where(UsageEvent.created_at >= since)
        .group_by(UsageEvent.provider)
    ).all()
    cap = get_settings().provider_daily_request_cap

    def count(stmt: object) -> int:
        return int(db.scalar(stmt) or 0)  # type: ignore[call-overload]

    n_user = select(func.count(User.id))
    return {
        "users": count(n_user),
        "verified_users": count(n_user.where(User.email_verified_at.is_not(None))),
        "suspended_users": count(n_user.where(User.suspended_at.is_not(None))),
        "active_today": count(
            select(func.count(func.distinct(UsageEvent.user_id))).where(
                UsageEvent.created_at >= since
            )
        ),
        "failed_runs_today": count(
            select(func.count(AgentRun.id)).where(
                AgentRun.status == "failed", AgentRun.created_at >= since
            )
        ),
        "usage_today": [
            {
                "provider": p,
                "requests": int(n),
                "tokens_in": int(ti or 0),
                "tokens_out": int(to or 0),
                "daily_cap": None if p == "mock" else cap,
            }
            for p, n, ti, to in usage
        ],
        "providers": [
            {
                "id": p.info.id,
                "name": p.info.name,
                "configured": p.configured(),
                "paid": p.info.paid,
            }
            for p in PROVIDERS.values()
        ],
        "paid_usage_enabled": get_settings().allow_paid_provider_usage,
    }


class UserOut(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    email_verified_at: datetime | None
    suspended_at: datetime | None
    created_at: datetime


@router.get("/users")
def users(
    admin: AdminUser,
    db: DbSession,
    q: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[UserOut]:
    stmt = select(User)
    if q:
        like = f"%{q.replace('%', '').replace('_', '')}%"
        stmt = stmt.where(or_(User.email.ilike(like), User.display_name.ilike(like)))
    rows = db.scalars(stmt.order_by(User.created_at.desc()).limit(limit).offset(offset))
    return [UserOut.model_validate(u, from_attributes=True) for u in rows]


class SuspendIn(BaseModel):
    suspended: bool
    reason: str = Field(default="", max_length=300)


@router.post("/users/{user_id}/suspend")
def suspend(user_id: UUID, body: SuspendIn, admin: AdminUser, db: DbSession) -> UserOut:
    user = db.get(User, user_id)
    if user is None:
        raise AppError("not_found", "User not found.", 404)
    if user.id == admin.id:
        raise AppError("forbidden", "You cannot suspend your own account.", 403)
    user.suspended_at = utcnow() if body.suspended else None
    if body.suspended:  # sign the user out everywhere immediately
        db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=utcnow())
        )
    audit(
        db,
        "admin.suspend" if body.suspended else "admin.unsuspend",
        admin,
        target=str(user.id),
        detail=body.reason or None,
    )
    return UserOut.model_validate(user, from_attributes=True)


@router.get("/audit")
def audit_events(
    admin: AdminUser, db: DbSession, limit: int = Query(default=100, le=500)
) -> list[dict[str, object]]:
    rows = db.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit))
    return [
        {
            "at": e.created_at.isoformat(),
            "actor": str(e.actor_id) if e.actor_id else None,
            "action": e.action,
            "target": e.target,
            "detail": e.detail,
        }
        for e in rows
    ]
