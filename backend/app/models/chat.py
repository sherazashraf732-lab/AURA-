from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base, IdMixin, TimestampMixin, utcnow


class Conversation(IdMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(200), default="New chat")
    provider: Mapped[str] = mapped_column(String(40), default="mock")
    model: Mapped[str] = mapped_column(String(120), default="aura-mock-1")
    archived_at: Mapped[datetime | None] = mapped_column(default=None)
    # Continuation chain (A1/A2): a new chat that continues from a summary of an older one.
    continued_from_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL")
    )
    continuation_summary_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_summaries.id", ondelete="SET NULL", use_alter=True)
    )
    language_override: Mapped[str | None] = mapped_column(String(16), default=None)

    __table_args__ = (Index("ix_conversations_owner_updated", "owner_id", "updated_at"),)


class Message(IdMixin, Base):
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    role: Mapped[str] = mapped_column(String(16))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(16), default=None)
    provider: Mapped[str | None] = mapped_column(String(40), default=None)
    model: Mapped[str | None] = mapped_column(String(120), default=None)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="complete")  # complete|error|stopped
    error_code: Mapped[str | None] = mapped_column(String(64), default=None)


class ConversationSummary(IdMixin, Base):
    """Temporary continuation summary. Never mixed with durable memory (spec 06)."""

    __tablename__ = "conversation_summaries"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    version: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[dict[str, object]] = mapped_column(JSONB)
    source_message_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))


class UserMemory(IdMixin, TimestampMixin, Base):
    """Durable user (project_id is null) or project memory (project_id set). User-controllable."""

    __tablename__ = "user_memories"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(16), default="user")  # user | suggested
    source_conversation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL")
    )
    enabled: Mapped[bool] = mapped_column(default=True)


class UsageEvent(IdMixin, Base):
    __tablename__ = "usage_events"

    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(32))  # chat | summary | search ...
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    ok: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        Index("ix_usage_user_time", "user_id", "created_at"),
        Index("ix_usage_provider_time", "provider", "created_at"),
    )
