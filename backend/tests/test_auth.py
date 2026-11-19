from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.identity import AuthSession, User
from tests.conftest import Api, last_link, make_user


def test_signup_verify_login_logout_flow(api: Api, db: Session) -> None:
    r = api.post("/auth/signup", {"email": "A@Example.com", "password": "correct-horse-1"})
    assert r.status_code == 202
    assert api.get("/auth/me").json() is None

    # Unverified users can sign in but are blocked from verified-only features.
    assert (
        api.post(
            "/auth/login", {"email": "a@example.com", "password": "correct-horse-1"}
        ).status_code
        == 200
    )
    assert api.get("/auth/me").json()["email_verified"] is False

    assert (
        api.post("/auth/verify-email", {"token": last_link(db, "a@example.com")}).status_code == 200
    )
    me = api.get("/auth/me").json()
    assert me["email"] == "a@example.com" and me["email_verified"] is True and me["role"] == "user"

    assert api.post("/auth/logout").status_code == 204
    assert api.get("/auth/me").json() is None


def test_token_reuse_and_bad_token_rejected(api: Api, db: Session) -> None:
    api.post("/auth/signup", {"email": "b@example.com", "password": "correct-horse-1"})
    token = last_link(db, "b@example.com")
    assert api.post("/auth/verify-email", {"token": token}).status_code == 200
    assert (
        api.post("/auth/verify-email", {"token": token}).json()["error"]["code"] == "invalid_token"
    )
    assert api.post("/auth/verify-email", {"token": "x" * 20}).status_code == 400


def test_login_errors_are_generic(api: Api) -> None:
    api.post("/auth/signup", {"email": "c@example.com", "password": "correct-horse-1"})
    wrong_pw = api.post("/auth/login", {"email": "c@example.com", "password": "nope-nope-nope"})
    no_user = api.post("/auth/login", {"email": "ghost@example.com", "password": "nope-nope-nope"})
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json()["error"]["message"] == no_user.json()["error"]["message"]


def test_duplicate_signup_does_not_reveal_account(api: Api, db: Session) -> None:
    first = api.post("/auth/signup", {"email": "d@example.com", "password": "correct-horse-1"})
    second = api.post("/auth/signup", {"email": "d@example.com", "password": "another-pass-22"})
    assert first.status_code == second.status_code == 202
    assert first.json() == second.json()
    assert len(db.scalars(select(User).where(User.email == "d@example.com")).all()) == 1


def test_weak_password_rejected(api: Api) -> None:
    r = api.post("/auth/signup", {"email": "e@example.com", "password": "short"})
    assert r.status_code == 422 and r.json()["error"]["code"] == "weak_password"


def test_csrf_required_for_state_changes(api: Api) -> None:
    r = api.c.post(
        "/api/v1/auth/signup", json={"email": "f@example.com", "password": "correct-horse-1"}
    )
    assert r.status_code == 403 and r.json()["error"]["code"] == "csrf_failed"
    r = api.c.post(
        "/api/v1/auth/signup",
        json={"email": "f@example.com", "password": "correct-horse-1"},
        headers={"x-csrf-token": "forged"},
    )
    assert r.status_code == 403


def test_password_reset_revokes_sessions_and_is_single_use(db: Session) -> None:
    user_api = make_user(db, "g@example.com")
    other = Api()
    assert other.post("/auth/request-password-reset", {"email": "g@example.com"}).status_code == 202
    token = last_link(db, "g@example.com")
    assert (
        other.post(
            "/auth/reset-password", {"token": token, "password": "brand-new-pass-9"}
        ).status_code
        == 200
    )
    assert (
        other.post(
            "/auth/reset-password", {"token": token, "password": "brand-new-pass-9"}
        ).status_code
        == 400
    )
    # Old session is revoked; new password works; old one does not.
    assert user_api.get("/auth/me").json() is None
    assert (
        other.post(
            "/auth/login", {"email": "g@example.com", "password": "correct-horse-1"}
        ).status_code
        == 401
    )
    assert (
        other.post(
            "/auth/login", {"email": "g@example.com", "password": "brand-new-pass-9"}
        ).status_code
        == 200
    )


def test_reset_request_for_unknown_email_looks_identical(api: Api) -> None:
    a = api.post("/auth/request-password-reset", {"email": "nobody@example.com"})
    api.post("/auth/signup", {"email": "h@example.com", "password": "correct-horse-1"})
    b = api.post("/auth/request-password-reset", {"email": "h@example.com"})
    assert a.status_code == b.status_code == 202 and a.json() == b.json()


def test_login_rate_limited(api: Api) -> None:
    codes = [
        api.post(
            "/auth/login", {"email": "i@example.com", "password": "wrong-password-x"}
        ).status_code
        for _ in range(9)
    ]
    assert codes[-1] == 429


def test_session_token_stored_hashed(db: Session) -> None:
    api = make_user(db, "j@example.com")
    raw = api.c.cookies.get("aura_session")
    assert raw
    hashes = [s.token_hash for s in db.scalars(select(AuthSession))]
    assert raw not in hashes and all(len(h) == 64 for h in hashes)


def test_bootstrap_admin_only_after_verification(api: Api, db: Session) -> None:
    api.post("/auth/signup", {"email": "admin@example.com", "password": "correct-horse-1"})
    api.post("/auth/login", {"email": "admin@example.com", "password": "correct-horse-1"})
    assert api.get("/auth/me").json()["role"] == "user"
    api.post("/auth/verify-email", {"token": last_link(db, "admin@example.com")})
    assert api.get("/auth/me").json()["role"] == "admin"


def test_profile_update(db: Session) -> None:
    api = make_user(db, "k@example.com")
    r = api.patch(
        "/auth/me", {"display_name": "Kay", "language_override": "ur-Latn", "memory_enabled": False}
    )
    assert r.status_code == 200
    me = r.json()
    assert (
        me["display_name"] == "Kay"
        and me["language_override"] == "ur-Latn"
        and me["memory_enabled"] is False
    )
    assert api.patch("/auth/me", {"language_override": "fr"}).status_code == 422
