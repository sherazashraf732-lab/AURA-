import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession, VerifiedUser
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.ratelimit import enforce
from app.models.data import Dataset
from app.models.identity import User
from app.services import data as svc

router = APIRouter(prefix="/data", tags=["data"])
MAX_DATASETS = 30


class DatasetOut(BaseModel):
    id: UUID
    name: str
    columns: list[str]
    row_count: int
    created_at: datetime


def _get(db: Session, user: User, dataset_id: UUID) -> Dataset:
    ds = db.scalar(select(Dataset).where(Dataset.id == dataset_id, Dataset.owner_id == user.id))
    if ds is None:
        raise AppError("not_found", "Dataset not found.", 404)
    return ds


@router.get("/datasets")
def list_datasets(user: CurrentUser, db: DbSession) -> list[DatasetOut]:
    rows = db.scalars(
        select(Dataset).where(Dataset.owner_id == user.id).order_by(Dataset.created_at.desc())
    )
    return [DatasetOut.model_validate(d, from_attributes=True) for d in rows]


@router.post("/datasets", status_code=201)
def import_dataset(
    file: UploadFile,
    request: Request,
    user: VerifiedUser,
    db: DbSession,
    trim: bool = True,
    drop_empty: bool = True,
    dedupe: bool = False,
) -> DatasetOut:
    enforce(request, "data-import", limit=30, window_s=3600, key=str(user.id))
    count = db.scalar(select(func.count(Dataset.id)).where(Dataset.owner_id == user.id)) or 0
    if count >= MAX_DATASETS:
        raise AppError("too_many_datasets", f"You can keep up to {MAX_DATASETS} datasets.", 409)
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise AppError("too_large", f"Files are limited to {get_settings().max_upload_mb} MB.", 413)
    columns, rows = svc.parse_table(file.filename or "", data)
    rows = svc.clean(rows, trim, drop_empty, dedupe)
    ds = Dataset(owner_id=user.id, name=(file.filename or "dataset")[-255:], columns=columns,
                 rows=rows, row_count=len(rows))  # fmt: skip
    db.add(ds)
    db.flush()
    return DatasetOut.model_validate(ds, from_attributes=True)


@router.get("/datasets/{dataset_id}")
def dataset_detail(dataset_id: UUID, user: CurrentUser, db: DbSession) -> dict[str, object]:
    ds = _get(db, user, dataset_id)
    return {
        **DatasetOut.model_validate(ds, from_attributes=True).model_dump(mode="json"),
        "preview": ds.rows[:50],
        "profile": svc.profile(ds.columns, ds.rows),
    }


@router.get("/datasets/{dataset_id}/chart")
def dataset_chart(
    dataset_id: UUID,
    user: CurrentUser,
    db: DbSession,
    x: str = Query(max_length=100),
    y: str | None = Query(default=None, max_length=100),
    agg: svc.Agg = "sum",
) -> dict[str, object]:
    ds = _get(db, user, dataset_id)
    return {"x": x, "y": y, "agg": agg, "source": ds.name,
            "points": svc.chart(ds.columns, ds.rows, x, y, agg)}  # fmt: skip


@router.get("/datasets/{dataset_id}/export")
def export_dataset(
    dataset_id: UUID, user: CurrentUser, db: DbSession, format: Literal["csv", "xlsx"] = "csv"
) -> Response:
    ds = _get(db, user, dataset_id)
    stem = re.sub(r"[^\w\- ]+", "", ds.name.rsplit(".", 1)[0])[:80] or "dataset"
    mime = "text/csv" if format == "csv" else (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  # fmt: skip
    disposition = f'attachment; filename="{stem}.{format}"'
    body = svc.export(ds.columns, ds.rows, format)
    return Response(body, media_type=mime, headers={"Content-Disposition": disposition})


@router.delete("/datasets/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: UUID, user: CurrentUser, db: DbSession) -> None:
    db.delete(_get(db, user, dataset_id))
