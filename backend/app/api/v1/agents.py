import json
import time
from collections.abc import Iterator
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession, VerifiedUser
from app.core.config import get_settings
from app.core.errors import AppError
from app.database.session import _session_factory
from app.models.agents import AgentRun, AgentStep
from app.models.identity import User
from app.modules.providers import get_provider, model_info
from app.modules.web import SEARCH_PROVIDERS, default_search
from app.services import chat as chat_svc
from app.services import research

router = APIRouter(tags=["agents"])


class RunIn(BaseModel):
    kind: Literal["research", "fact_check"]
    text: str = Field(min_length=3, max_length=2000)
    provider: str = "mock"
    model: str = "aura-mock-1"
    search_provider: str | None = None
    project_id: UUID | None = None


class StepOut(BaseModel):
    seq: int
    name: str
    tool: str | None
    status: str
    summary: str
    created_at: datetime
    finished_at: datetime | None


class RunOut(BaseModel):
    id: UUID
    kind: str
    title: str
    provider: str
    model: str
    search_provider: str
    status: str
    current_step: str | None
    progress: int | None
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    result: dict[str, object] | None
    steps: list[StepOut] = []


def _out(db: Session, run: AgentRun, with_steps: bool = True) -> RunOut:
    out = RunOut.model_validate(run, from_attributes=True)
    if with_steps:
        out.steps = [
            StepOut.model_validate(s, from_attributes=True)
            for s in db.scalars(
                select(AgentStep).where(AgentStep.run_id == run.id).order_by(AgentStep.seq)
            )
        ]
    return out


def _run(db: Session, user: User, run_id: UUID) -> AgentRun:
    run = db.scalar(select(AgentRun).where(AgentRun.id == run_id, AgentRun.owner_id == user.id))
    if run is None:
        raise AppError("not_found", "Run not found.", 404)
    return run


@router.get("/search-providers")
def search_providers(user: CurrentUser) -> list[dict[str, object]]:
    return [
        {"id": p.id, "name": p.name, "available": p.configured()} for p in SEARCH_PROVIDERS.values()
    ]


@router.post("/agent-runs", status_code=201)
def create_run(body: RunIn, user: VerifiedUser, db: DbSession) -> RunOut:
    provider = get_provider(body.provider)
    model_info(provider, body.model)
    search = SEARCH_PROVIDERS.get(body.search_provider or "") or default_search()
    if not search.configured():
        raise AppError("search_unconfigured", f"{search.name} is not configured.", 503)
    if body.project_id:
        chat_svc.get_project(db, user, body.project_id)
    if provider.info.requires_consent and user.provider_consent_at is None:
        raise AppError("consent_required", "Please accept the external provider terms first.", 403)
    if not provider.configured():
        raise AppError("provider_unconfigured", f"{provider.info.name} is not configured.", 503)
    active = db.scalar(
        select(func.count(AgentRun.id)).where(
            AgentRun.owner_id == user.id, AgentRun.status.in_(("queued", "running"))
        )
    )
    if (active or 0) >= get_settings().max_concurrent_jobs_per_user:
        raise AppError("too_many_runs", "Wait for your running tasks to finish.", 429)
    chat_svc.check_quota(db, user, body.provider)
    run = AgentRun(owner_id=user.id, project_id=body.project_id, kind=body.kind,
                   title=body.text.strip().splitlines()[0][:300], input={"text": body.text},
                   provider=body.provider, model=body.model, search_provider=search.id)  # fmt: skip
    db.add(run)
    db.commit()
    research.start(run.id)
    return _out(db, run)


@router.get("/agent-runs")
def list_runs(
    user: CurrentUser,
    db: DbSession,
    kind: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
) -> list[RunOut]:
    q = select(AgentRun).where(AgentRun.owner_id == user.id)
    if kind:
        q = q.where(AgentRun.kind == kind)
    return [
        _out(db, r, with_steps=False)
        for r in db.scalars(q.order_by(AgentRun.created_at.desc()).limit(limit))
    ]


@router.get("/agent-runs/{run_id}")
def get_run(run_id: UUID, user: CurrentUser, db: DbSession) -> RunOut:
    return _out(db, _run(db, user, run_id))


@router.post("/agent-runs/{run_id}/cancel")
def cancel_run(run_id: UUID, user: CurrentUser, db: DbSession) -> RunOut:
    run = _run(db, user, run_id)
    if run.status in ("queued", "running"):
        run.cancel_requested = True
    return _out(db, run)


@router.delete("/agent-runs/{run_id}", status_code=204)
def delete_run(run_id: UUID, user: CurrentUser, db: DbSession) -> None:
    run = _run(db, user, run_id)
    if run.status in ("queued", "running"):
        raise AppError("run_active", "Cancel the run before deleting it.", 409)
    db.delete(run)


@router.get("/agent-runs/{run_id}/events")
def run_events(run_id: UUID, user: CurrentUser, db: DbSession) -> StreamingResponse:
    _run(db, user, run_id)  # authorise before streaming
    owner = user.id

    def gen() -> Iterator[str]:
        last = ""
        for _ in range(600):  # hard stop after ~10 minutes
            s = _session_factory()()
            try:
                run = s.scalar(
                    select(AgentRun).where(AgentRun.id == run_id, AgentRun.owner_id == owner)
                )
                if run is None:
                    return
                payload = _out(s, run).model_dump_json()
            finally:
                s.close()
            if payload != last:
                last = payload
                yield f"event: run\ndata: {payload}\n\n"
            if json.loads(payload)["status"] not in ("queued", "running"):
                return
            yield ": heartbeat\n\n"
            time.sleep(1)

    return StreamingResponse(
        gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )
