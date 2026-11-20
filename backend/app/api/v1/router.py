from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.deps import DbSession, check_csrf
from app.api.v1 import agents, auth, chat, projects

api_router = APIRouter(dependencies=[Depends(check_csrf)])


@api_router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/health/ready", tags=["system"])
def ready(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}


api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(projects.router)
api_router.include_router(agents.router)
