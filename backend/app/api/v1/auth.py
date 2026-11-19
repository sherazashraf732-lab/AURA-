from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import CSRF_COOKIE, SESSION_COOKIE, CurrentUser, DbSession, OptionalUser
from app.core.config import get_settings
from app.core.ratelimit import enforce
from app.core.security import new_token
from app.database.session import utcnow
from app.models.identity import User
from app.services import auth as svc

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
    display_name: str = Field(default="", max_length=80)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class EmailIn(BaseModel):
    email: EmailStr


class TokenIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)


class ResetIn(TokenIn):
    password: str = Field(min_length=1, max_length=256)


class MeOut(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    email_verified: bool
    language_override: str | None
    memory_enabled: bool
    auto_continuation: bool
    provider_consent_at: datetime | None

    @classmethod
    def of(cls, u: User) -> "MeOut":
        return cls(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            role=u.role,
            email_verified=u.is_verified,
            language_override=u.language_override,
            memory_enabled=u.memory_enabled,
            auto_continuation=u.auto_continuation,
            provider_consent_at=u.provider_consent_at,
        )


class Message(BaseModel):
    message: str


def _set_csrf(response: Response) -> str:
    token = new_token()
    response.set_cookie(
        CSRF_COOKIE,
        token,
        httponly=False,
        samesite="lax",
        secure=get_settings().is_production,
        path="/",
    )
    return token


@router.get("/csrf")
def csrf(response: Response) -> dict[str, str]:
    return {"csrf_token": _set_csrf(response)}


@router.post("/signup", status_code=202)
def signup(body: SignupIn, request: Request, db: DbSession) -> Message:
    enforce(request, "signup", limit=5, window_s=3600)
    svc.signup(db, body.email, body.password, body.display_name)
    return Message(message="Check your email to verify your account.")


@router.post("/verify-email")
def verify_email(body: TokenIn, db: DbSession) -> Message:
    svc.verify_email(db, body.token)
    return Message(message="Email verified.")


@router.post("/resend-verification", status_code=202)
def resend(body: EmailIn, request: Request, db: DbSession) -> Message:
    enforce(request, "resend", limit=3, window_s=3600)
    svc.resend_verification(db, body.email)
    return Message(message="If the account needs verification, a new email was sent.")


@router.post("/login")
def login(body: LoginIn, request: Request, response: Response, db: DbSession) -> MeOut:
    enforce(request, "login-ip", limit=20, window_s=900)
    enforce(request, "login-email", limit=8, window_s=900, key=body.email.lower())
    user, token = svc.login(db, body.email, body.password, request.headers.get("user-agent"))
    s = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=s.is_production,
        max_age=s.session_ttl_hours * 3600,
        path="/",
    )
    _set_csrf(response)  # rotate CSRF token on privilege change
    return MeOut.of(user)


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: DbSession) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        svc.logout(db, token)
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/me")
def me(user: OptionalUser, request: Request, response: Response) -> MeOut | None:
    if CSRF_COOKIE not in request.cookies:
        _set_csrf(response)
    return MeOut.of(user) if user else None


@router.post("/request-password-reset", status_code=202)
def request_reset(body: EmailIn, request: Request, db: DbSession) -> Message:
    enforce(request, "reset", limit=5, window_s=3600)
    svc.request_password_reset(db, body.email)
    return Message(message="If an account exists for that email, a reset link was sent.")


@router.post("/reset-password")
def reset_password(body: ResetIn, request: Request, db: DbSession) -> Message:
    enforce(request, "reset-confirm", limit=10, window_s=3600)
    svc.reset_password(db, body.token, body.password)
    return Message(message="Password updated. Please sign in.")


class ProfileIn(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    language_override: str | None = Field(default=None, pattern=r"^(auto|en|ur|ur-Latn)$")
    memory_enabled: bool | None = None
    auto_continuation: bool | None = None
    provider_consent: bool | None = None


@router.patch("/me")
def update_me(body: ProfileIn, user: CurrentUser, db: DbSession) -> MeOut:
    if body.display_name is not None:
        user.display_name = body.display_name.strip()
    if body.language_override is not None:
        user.language_override = (
            None if body.language_override == "auto" else body.language_override
        )
    if body.memory_enabled is not None:
        user.memory_enabled = body.memory_enabled
    if body.auto_continuation is not None:
        user.auto_continuation = body.auto_continuation
    if body.provider_consent is not None:
        user.provider_consent_at = utcnow() if body.provider_consent else None
        svc.audit(db, "user.provider_consent", user, detail=str(body.provider_consent))
    return MeOut.of(user)
