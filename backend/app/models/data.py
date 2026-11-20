from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base, IdMixin, utcnow


class Dataset(IdMixin, Base):
    """A user's imported table, stored as JSONB (bounded by Data Studio's row/column limits)."""

    __tablename__ = "datasets"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    columns: Mapped[list[str]] = mapped_column(JSONB)
    rows: Mapped[list[list[str]]] = mapped_column(JSONB)
    row_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
