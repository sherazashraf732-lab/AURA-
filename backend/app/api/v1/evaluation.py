"""Model Arena (A4) and Evaluation Center (M20/A5): one shared engine (decision C6).

Arena: the same prompt to up to 3 models side by side, with latency and token usage.
Evaluation: repeatable test sets (input + expected text) scored against a model.
No objective quality ranking is claimed; scores are exactly what the user's test cases check.
"""

import time
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.api.deps import CurrentUser, DbSession, VerifiedUser
from app.core.errors import AppError
from app.database.session import Base, IdMixin, utcnow
from app.models.chat import UsageEvent
from app.modules.providers import ChatMessage, StreamResult, get_provider, model_info
from app.services import chat as chat_svc

router = APIRouter(tags=["evaluation"])


class EvalDataset(IdMixin, Base):
    __tablename__ = "eval_datasets"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    cases: Mapped[list[dict[str, str]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class EvalRun(IdMixin, Base):
    __tablename__ = "eval_runs"

    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("eval_datasets.id", ondelete="CASCADE"))
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    system_prompt: Mapped[str] = mapped_column(String(4000), default="")
    passed: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    avg_latency_ms: Mapped[int] = mapped_column(Integer)
    results: Mapped[list[dict[str, object]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Contender(BaseModel):
    provider: str
    model: str


def _call(
    db: DbSession, user_id: UUID, kind: str, c: Contender, system: str, prompt: str
) -> dict[str, object]:
    p = get_provider(c.provider)
    model_info(p, c.model)
    res = StreamResult()
    t0 = time.monotonic()
    try:
        text = "".join(
            p.stream(c.model, [ChatMessage("system", system), ChatMessage("user", prompt)], res)
        )
        err = None
    except AppError as e:
        text, err = "", e.message
    ms = int((time.monotonic() - t0) * 1000)
    db.add(
        UsageEvent(
            user_id=user_id,
            kind=kind,
            provider=c.provider,
            model=c.model,
            tokens_in=res.tokens_in,
            tokens_out=res.tokens_out,
            latency_ms=ms,
            ok=err is None,
        )
    )
    return {
        "provider": c.provider,
        "model": c.model,
        "served_by": res.served_by or None,
        "output": text,
        "error": err,
        "latency_ms": ms,
        "tokens_in": res.tokens_in,
        "tokens_out": res.tokens_out,
    }


class ArenaIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    contenders: list[Contender] = Field(min_length=2, max_length=3)


@router.post("/arena")
def arena(body: ArenaIn, user: VerifiedUser, db: DbSession) -> dict[str, object]:
    for c in body.contenders:  # every provider must pass consent/quota before any call is made
        chat_svc.ensure_provider_usable(db, user, c.provider)
    system = "You are a helpful assistant. Answer the user's prompt."
    return {
        "results": [_call(db, user.id, "arena", c, system, body.prompt) for c in body.contenders],
        "note": "Side-by-side outputs only; no automatic quality ranking.",
    }


class Case(BaseModel):
    input: str = Field(min_length=1, max_length=4000)
    expected: str = Field(min_length=1, max_length=500)  # case-insensitive substring check


class DatasetIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    cases: list[Case] = Field(min_length=1, max_length=50)


def _ds(db: DbSession, user_id: UUID, did: UUID) -> EvalDataset:
    ds = db.scalar(
        select(EvalDataset).where(EvalDataset.id == did, EvalDataset.owner_id == user_id)
    )
    if ds is None:
        raise AppError("not_found", "Test set not found.", 404)
    return ds


@router.get("/evaluations/datasets")
def list_datasets(user: CurrentUser, db: DbSession) -> list[dict[str, object]]:
    rows = db.scalars(
        select(EvalDataset)
        .where(EvalDataset.owner_id == user.id)
        .order_by(EvalDataset.created_at.desc())
    )
    return [{"id": str(d.id), "name": d.name, "cases": d.cases} for d in rows]


@router.post("/evaluations/datasets", status_code=201)
def create_dataset(body: DatasetIn, user: VerifiedUser, db: DbSession) -> dict[str, object]:
    ds = EvalDataset(owner_id=user.id, name=body.name, cases=[c.model_dump() for c in body.cases])
    db.add(ds)
    db.flush()
    return {"id": str(ds.id), "name": ds.name, "cases": ds.cases}


@router.delete("/evaluations/datasets/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: UUID, user: CurrentUser, db: DbSession) -> None:
    db.delete(_ds(db, user.id, dataset_id))


class EvalIn(BaseModel):
    provider: str = "mock"
    model: str = "aura-mock-1"
    system_prompt: str = Field(default="Answer concisely.", max_length=4000)


@router.post("/evaluations/datasets/{dataset_id}/runs", status_code=201)
def run_eval(
    dataset_id: UUID, body: EvalIn, user: VerifiedUser, db: DbSession
) -> dict[str, object]:
    ds = _ds(db, user.id, dataset_id)
    chat_svc.ensure_provider_usable(db, user, body.provider)
    c = Contender(provider=body.provider, model=body.model)
    results = []
    for case in ds.cases:
        r = _call(db, user.id, "evaluation", c, body.system_prompt, case["input"])
        r["expected"] = case["expected"]
        r["passed"] = r["error"] is None and case["expected"].lower() in str(r["output"]).lower()
        results.append(r)
    run = EvalRun(
        dataset_id=ds.id,
        owner_id=user.id,
        provider=c.provider,
        model=c.model,
        system_prompt=body.system_prompt,
        passed=sum(1 for r in results if r["passed"]),
        total=len(results),
        results=results,
        avg_latency_ms=sum(int(str(r["latency_ms"])) for r in results) // len(results),
    )
    db.add(run)
    db.flush()
    return _run_out(run)


def _run_out(r: EvalRun) -> dict[str, object]:
    return {
        "id": str(r.id),
        "provider": r.provider,
        "model": r.model,
        "passed": r.passed,
        "total": r.total,
        "avg_latency_ms": r.avg_latency_ms,
        "results": r.results,
        "created_at": r.created_at.isoformat(),
    }


@router.get("/evaluations/datasets/{dataset_id}/runs")
def list_runs(dataset_id: UUID, user: CurrentUser, db: DbSession) -> list[dict[str, object]]:
    ds = _ds(db, user.id, dataset_id)
    rows = db.scalars(
        select(EvalRun)
        .where(EvalRun.dataset_id == ds.id)
        .order_by(EvalRun.created_at.desc())
        .limit(20)
    )
    return [_run_out(r) for r in rows]
