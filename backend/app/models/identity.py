from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base, IdMixin, TimestampMixin, utcnow


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(16), default="user")  # user | admin
    email_verified_at: Mapped[datetime | None] = mapped_column(default=None)
    suspended_at: Mapped[datetime | None] = mapped_column(default=None)
    # Personalisation
    language_override: Mapped[str | None] = mapped_column(String(16), default=None)
    memory_enabled: Mapped[bool] = mapped_column(default=True)
    auto_continuation: Mapped[bool] = mapped_column(default=True)
    provider_consent_at: Mapped[datetime | None] = mapped_column(default=None)

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class AuthSession(IdMixin, Base):
    __tablename__ = "auth_sessions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(default=utcnow)
    expires_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None] = mapped_column(default=None)
    user_agent: Mapped[str | None] = mapped_column(String(255), default=None)


class EmailToken(IdMixin, Base):
    __tablename__ = "email_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(String(16))  # verify | reset
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    expires_at: Mapped[datetime]
    used_at: Mapped[datetime | None] = mapped_column(default=None)


class Workspace(IdMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Project(IdMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    instructions: Mapped[str] = mapped_column(Text, default="")
    archived_at: Mapped[datetime | None] = mapped_column(default=None)

    __table_args__ = (Index("ix_projects_owner_updated", "owner_id", "updated_at"),)


class AuditEvent(IdMixin, Base):
    """Append-only security/admin audit trail. Never store secrets or message content here."""

    __tablename__ = "audit_events"

    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(64))
    target: Mapped[str | None] = mapped_column(String(120), default=None)
    detail: Mapped[str | None] = mapped_column(String(500), default=None)


class OutboxEmail(IdMixin, Base):
    """Dev/test mail sink: verification and reset links are inspectable without a provider."""

    __tablename__ = "outbox_emails"

    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    to_email: Mapped[str] = mapped_column(String(320), index=True)
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
