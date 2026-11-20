from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.identity import User
from tests.conftest import Api, last_link, make_user


def admin_api(db: Session) -> Api:
    return make_user(db, "admin@example.com")  # BOOTSTRAP_ADMIN_EMAIL in conftest


def test_admin_routes_require_admin(db: Session) -> None:
    user = make_user(db, "plain@example.com")
    for path in ("/admin/stats", "/admin/users", "/admin/audit"):
        assert user.get(path).status_code == 403
    assert Api().get("/admin/stats").status_code == 401


def test_stats_users_and_suspend(db: Session) -> None:
    admin = admin_api(db)
    victim = make_user(db, "v@example.com")
    victim.post("/conversations", {"provider": "mock", "model": "aura-mock-1"})
    s = admin.get("/admin/stats").json()
    assert s["users"] == 2 and s["paid_usage_enabled"] is False
    assert any(p["id"] == "auto" for p in s["providers"])
    vid = next(u["id"] for u in admin.get("/admin/users?q=v@").json())
    assert (
        admin.post(f"/admin/users/{vid}/suspend", {"suspended": True, "reason": "spam"}).status_code
        == 200
    )
    assert victim.get("/auth/me").json() is None  # signed out everywhere
    r = Api().post("/auth/login", {"email": "v@example.com", "password": "correct-horse-1"})
    assert r.status_code == 403 and r.json()["error"]["code"] == "account_suspended"
    admin.post(f"/admin/users/{vid}/suspend", {"suspended": False})
    assert (
        Api()
        .post("/auth/login", {"email": "v@example.com", "password": "correct-horse-1"})
        .status_code
        == 200
    )
    me = admin.get("/auth/me").json()["id"]
    assert admin.post(f"/admin/users/{me}/suspend", {"suspended": True}).status_code == 403
    assert "admin.suspend" in [e["action"] for e in admin.get("/admin/audit").json()]


def test_signup_requires_terms_and_honeypot_blocks_bots(api: Api, db: Session) -> None:
    r = api.post("/auth/signup", {"email": "t@example.com", "password": "correct-horse-1"})
    assert r.status_code == 422 and r.json()["error"]["code"] == "terms_required"
    bot = api.post(
        "/auth/signup",
        {
            "email": "bot@example.com",
            "password": "correct-horse-1",
            "accept_terms": True,
            "website": "http://spam",
        },
    )
    assert bot.status_code == 202
    assert db.scalar(select(User).where(User.email == "bot@example.com")) is None
    ok = api.post(
        "/auth/signup",
        {"email": "t@example.com", "password": "correct-horse-1", "accept_terms": True},
    )
    assert ok.status_code == 202 and last_link(db, "t@example.com")
