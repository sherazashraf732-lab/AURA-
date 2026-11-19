from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.database.session import utcnow
from app.models.identity import Project, Workspace
from app.services.chat import get_project

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    instructions: str = Field(default="", max_length=8000)


class ProjectPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    instructions: str | None = Field(default=None, max_length=8000)
    archived: bool | None = None


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str
    instructions: str
    archived: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def of(cls, p: Project) -> "ProjectOut":
        return cls(
            id=p.id,
            name=p.name,
            description=p.description,
            instructions=p.instructions,
            archived=p.archived_at is not None,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )


@router.get("")
def list_projects(user: CurrentUser, db: DbSession, archived: bool = False) -> list[ProjectOut]:
    q = select(Project).where(Project.owner_id == user.id)
    q = q.where(Project.archived_at.is_not(None) if archived else Project.archived_at.is_(None))
    return [ProjectOut.of(p) for p in db.scalars(q.order_by(Project.updated_at.desc()))]


@router.post("", status_code=201)
def create_project(body: ProjectIn, user: CurrentUser, db: DbSession) -> ProjectOut:
    ws = db.scalar(select(Workspace).where(Workspace.owner_id == user.id))
    if ws is None:
        ws = Workspace(owner_id=user.id, name="Personal")
        db.add(ws)
        db.flush()
    p = Project(workspace_id=ws.id, owner_id=user.id, **body.model_dump())
    db.add(p)
    db.flush()
    return ProjectOut.of(p)


@router.get("/{project_id}")
def read_project(project_id: UUID, user: CurrentUser, db: DbSession) -> ProjectOut:
    return ProjectOut.of(get_project(db, user, project_id))


@router.patch("/{project_id}")
def update_project(
    project_id: UUID, body: ProjectPatch, user: CurrentUser, db: DbSession
) -> ProjectOut:
    p = get_project(db, user, project_id)
    for k in ("name", "description", "instructions"):
        v = getattr(body, k)
        if v is not None:
            setattr(p, k, v)
    if body.archived is not None:
        p.archived_at = utcnow() if body.archived else None
    p.updated_at = utcnow()
    return ProjectOut.of(p)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: UUID, user: CurrentUser, db: DbSession) -> None:
    db.delete(get_project(db, user, project_id))
