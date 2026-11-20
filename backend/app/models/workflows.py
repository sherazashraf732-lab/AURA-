from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base, IdMixin, TimestampMixin, utcnow


class Workflow(IdMixin, TimestampMixin, Base):
    """A user-defined sequence of typed steps (M12). `steps` is validated by the API schema."""

    __tablename__ = "workflows"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    version: Mapped[int] = mapped_column(Integer, default=1)
    steps: Mapped[list[dict[str, object]]] = mapped_column(JSONB)
    provider: Mapped[str] = mapped_column(String(40), default="mock")
    model: Mapped[str] = mapped_column(String(120), default="aura-mock-1")


class WorkflowRun(IdMixin, Base):
    __tablename__ = "workflow_runs"

    workflow_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    workflow_version: Mapped[int] = mapped_column(Integer)
    steps: Mapped[list[dict[str, object]]] = mapped_column(JSONB)  # snapshot at start
    input: Mapped[str] = mapped_column(String(8000))
    # running | waiting_for_approval | succeeded | failed | rejected
    status: Mapped[str] = mapped_column(String(24), default="running")
    step_index: Mapped[int] = mapped_column(Integer, default=0)
    log: Mapped[list[dict[str, object]]] = mapped_column(JSONB, default=list)
    error: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)
