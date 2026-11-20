from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base, IdMixin, utcnow


class KnowledgeSource(IdMixin, Base):
    """An uploaded document. Only extracted text is kept (no original file bytes)."""

    __tablename__ = "knowledge_sources"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    filename: Mapped[str] = mapped_column(String(255))
    kind: Mapped[str] = mapped_column(String(16))  # txt | md | csv | pdf | docx
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class DocumentChunk(IdMixin, Base):
    __tablename__ = "document_chunks"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_sources.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    seq: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)

    # 'simple' config: no stemming/stop-words, so Urdu script and Roman Urdu are indexed as-is.
    __table_args__ = (
        Index(
            "ix_document_chunks_fts",
            sql_text("to_tsvector('simple'::regconfig, text)"),
            postgresql_using="gin",
        ),
        Index("ix_document_chunks_owner", "owner_id"),
    )
