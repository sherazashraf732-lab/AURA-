from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Query, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, VerifiedUser
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.ratelimit import enforce
from app.models.knowledge import KnowledgeSource
from app.services import chat as chat_svc
from app.services import knowledge as svc

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
MAX_SOURCES = 100


class SourceOut(BaseModel):
    id: UUID
    filename: str
    kind: str
    size_bytes: int
    char_count: int
    chunk_count: int
    project_id: UUID | None
    created_at: datetime


@router.get("/sources")
def list_sources(user: CurrentUser, db: DbSession) -> list[SourceOut]:
    rows = db.scalars(
        select(KnowledgeSource)
        .where(KnowledgeSource.owner_id == user.id)
        .order_by(KnowledgeSource.created_at.desc())
    )
    return [SourceOut.model_validate(s, from_attributes=True) for s in rows]


@router.post("/sources", status_code=201)
def upload(
    file: UploadFile,
    request: Request,
    user: VerifiedUser,
    db: DbSession,
    project_id: Annotated[UUID | None, Form()] = None,
) -> SourceOut:
    enforce(request, "upload", limit=30, window_s=3600, key=str(user.id))
    if svc.source_count(db, user) >= MAX_SOURCES:
        raise AppError("too_many_files", f"You can keep up to {MAX_SOURCES} documents.", 409)
    if project_id:
        chat_svc.get_project(db, user, project_id)
    limit = get_settings().max_upload_mb * 1024 * 1024
    # Sync endpoint (runs in a threadpool) so PDF parsing never blocks the event loop.
    data = file.file.read(limit + 1)  # never read more than the limit into memory
    src = svc.ingest(db, user, file.filename or "upload.txt", data, project_id)
    return SourceOut.model_validate(src, from_attributes=True)


@router.delete("/sources/{source_id}", status_code=204)
def delete_source(source_id: UUID, user: CurrentUser, db: DbSession) -> None:
    src = db.scalar(
        select(KnowledgeSource).where(
            KnowledgeSource.id == source_id, KnowledgeSource.owner_id == user.id
        )
    )
    if src is None:
        raise AppError("not_found", "Document not found.", 404)
    db.delete(src)


@router.get("/search")
def search(
    user: CurrentUser, db: DbSession, q: str = Query(min_length=2, max_length=500)
) -> list[dict[str, object]]:
    return [
        {
            "source_id": str(h.source_id),
            "filename": h.filename,
            "part": h.seq + 1,
            "excerpt": h.text[:400],
            "rank": round(h.rank, 4),
        }
        for h in svc.search(db, user, q)
    ]


class AskIn(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    provider: str = "mock"
    model: str = "aura-mock-1"
    source_ids: list[UUID] | None = None


@router.post("/ask")
def ask(body: AskIn, request_user: VerifiedUser, db: DbSession) -> dict[str, object]:
    chat_svc.ensure_provider_usable(db, request_user, body.provider)
    return svc.answer(db, request_user, body.question, body.provider, body.model, body.source_ids)
