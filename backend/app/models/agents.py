from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base, IdMixin, utcnow


class AgentRun(IdMixin, Base):
    """One bounded agent task (e.g. a research run), shown live in the Agent Control Room (A3)."""

    __tablename__ = "agent_runs"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    kind: Mapped[str] = mapped_column(String(32))  # research | fact_check
    title: Mapped[str] = mapped_column(String(300))
    input: Mapped[dict[str, object]] = mapped_column(JSONB)
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    search_provider: Mapped[str] = mapped_column(String(40))
    # queued | running | succeeded | failed | cancelled
    status: Mapped[str] = mapped_column(String(16), default="queued")
    current_step: Mapped[str | None] = mapped_column(String(120), default=None)
    progress: Mapped[int | None] = mapped_column(Integer, default=None)  # only when measurable
    cancel_requested: Mapped[bool] = mapped_column(default=False)
    error: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(default=None)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)
    result: Mapped[dict[str, object] | None] = mapped_column(JSONB, default=None)

    __table_args__ = (Index("ix_agent_runs_owner_created", "owner_id", "created_at"),)


class AgentStep(IdMixin, Base):
    __tablename__ = "agent_steps"

    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True
    )
    seq: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(120))
    tool: Mapped[str | None] = mapped_column(String(60), default=None)
    status: Mapped[str] = mapped_column(String(16), default="running")  # running|ok|error|skipped
    summary: Mapped[str] = mapped_column(
        Text, default=""
    )  # concise action summary, no raw reasoning
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)
