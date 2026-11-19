import os
import re
from collections.abc import Iterator

import pytest

# Tests always run against a disposable PostgreSQL database, never the dev database.
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://aura:aura@127.0.0.1:5433/aura_test"),
)
os.environ["APP_ENV"] = "test"
os.environ["BOOTSTRAP_ADMIN_EMAIL"] = "admin@example.com"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

import app.models  # noqa: E402,F401
from app.core.ratelimit import limiter  # noqa: E402
from app.database.session import Base, _session_factory, get_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.identity import OutboxEmail  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _schema() -> Iterator[None]:
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    yield
    limiter.reset()
    tables = ", ".join(f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables))
    with get_engine().begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
def db() -> Iterator[Session]:
    s = _session_factory()()
    yield s
    s.close()


class Api:
    """TestClient wrapper that performs the CSRF double-submit like the real frontend."""

    def __init__(self) -> None:
        self.c = TestClient(app)
        self.csrf = self.c.get("/api/v1/auth/csrf").json()["csrf_token"]

    def _h(self) -> dict[str, str]:
        self.csrf = self.c.cookies.get("aura_csrf") or self.csrf
        return {"x-csrf-token": self.csrf}

    def get(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self.c.get(f"/api/v1{path}", **kw)

    def post(self, path: str, json: object = None, **kw):  # type: ignore[no-untyped-def]
        return self.c.post(f"/api/v1{path}", json=json, headers=self._h(), **kw)

    def patch(self, path: str, json: object = None):  # type: ignore[no-untyped-def]
        return self.c.patch(f"/api/v1{path}", json=json, headers=self._h())

    def put(self, path: str, json: object = None):  # type: ignore[no-untyped-def]
        return self.c.put(f"/api/v1{path}", json=json, headers=self._h())

    def delete(self, path: str):  # type: ignore[no-untyped-def]
        return self.c.delete(f"/api/v1{path}", headers=self._h())


def last_link(db: Session, email: str) -> str:
    db.expire_all()
    mail = db.scalars(
        select(OutboxEmail).where(OutboxEmail.to_email == email).order_by(OutboxEmail.created_at.desc())
    ).first()
    assert mail is not None
    m = re.search(r"token=([\w\-]+)", mail.body)
    assert m
    return m.group(1)


def make_user(db: Session, email: str = "user@example.com", password: str = "correct-horse-1") -> Api:
    api = Api()
    assert api.post("/auth/signup", {"email": email, "password": password}).status_code == 202
    assert api.post("/auth/verify-email", {"token": last_link(db, email)}).status_code == 200
    assert api.post("/auth/login", {"email": email, "password": password}).status_code == 200
    return api


@pytest.fixture
def api() -> Api:
    return Api()
