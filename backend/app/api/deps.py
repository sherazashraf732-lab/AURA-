from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import tokens_equal
from app.database.session import get_db
from app.models.identity import User
from app.services import auth as auth_service

SESSION_COOKIE = "aura_session"
CSRF_COOKIE = "aura_csrf"
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

DbSession = Annotated[Session, Depends(get_db)]


def check_csrf(request: Request) -> None:
    """Double-submit CSRF check for every state-changing request (cookies are SameSite=Lax too)."""
    if request.method not in UNSAFE_METHODS:
        return
    cookie = request.cookies.get(CSRF_COOKIE)
    header = request.headers.get("x-csrf-token")
    if not cookie or not header or not tokens_equal(cookie, header):
        raise AppError("csrf_failed", "Security check failed. Refresh the page and try again.", 403)


def optional_user(request: Request, db: DbSession) -> User | None:
    token = request.cookies.get(SESSION_COOKIE)
    return auth_service.session_user(db, token) if token else None


def current_user(user: Annotated[User | None, Depends(optional_user)]) -> User:
    if user is None:
        raise AppError("unauthenticated", "Please sign in.", 401)
    return user


def verified_user(user: Annotated[User, Depends(current_user)]) -> User:
    if not user.is_verified:
        raise AppError("email_unverified", "Verify your email to use this feature.", 403)
    return user


def admin_user(user: Annotated[User, Depends(verified_user)]) -> User:
    if not user.is_admin:
        raise AppError("forbidden", "Administrator access required.", 403)
    return user


CurrentUser = Annotated[User, Depends(current_user)]
VerifiedUser = Annotated[User, Depends(verified_user)]
AdminUser = Annotated[User, Depends(admin_user)]
OptionalUser = Annotated[User | None, Depends(optional_user)]
