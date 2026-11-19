from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import hash_password, hash_token, needs_rehash, new_token, verify_password
from app.database.session import utcnow
from app.models.identity import AuditEvent, AuthSession, EmailToken, User, Workspace
from app.services.mailer import get_mailer

GENERIC_LOGIN_ERROR = "Email or password is incorrect."


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_password(password: str, email: str) -> None:
    if len(password) < 10:
        raise AppError("weak_password", "Password must be at least 10 characters.", 422)
    if len(password) > 128:
        raise AppError("weak_password", "Password must be at most 128 characters.", 422)
    local = email.split("@")[0]
    if len(local) >= 4 and local in password.lower():
        raise AppError("weak_password", "Password must not contain your email name.", 422)


def audit(
    db: Session,
    action: str,
    actor: User | None = None,
    target: str | None = None,
    detail: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_id=actor.id if actor else None, action=action, target=target, detail=detail
        )
    )


def _as_aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _issue_email_token(db: Session, user: User, purpose: str, ttl: timedelta) -> str:
    # Invalidate earlier unused tokens of the same purpose: only the newest link works.
    db.execute(
        update(EmailToken)
        .where(
            EmailToken.user_id == user.id,
            EmailToken.purpose == purpose,
            EmailToken.used_at.is_(None),
        )
        .values(used_at=utcnow())
    )
    token = new_token()
    db.add(
        EmailToken(
            user_id=user.id,
            purpose=purpose,
            token_hash=hash_token(token),
            expires_at=utcnow() + ttl,
        )
    )
    return token


def _consume_email_token(db: Session, token: str, purpose: str) -> User:
    row = db.scalar(
        select(EmailToken).where(
            EmailToken.token_hash == hash_token(token), EmailToken.purpose == purpose
        )
    )
    if row is None or row.used_at is not None or _as_aware(row.expires_at) < utcnow():
        raise AppError("invalid_token", "This link is invalid or has expired.", 400)
    row.used_at = utcnow()
    user = db.get(User, row.user_id)
    if user is None:
        raise AppError("invalid_token", "This link is invalid or has expired.", 400)
    return user


def send_verification(db: Session, user: User) -> None:
    s = get_settings()
    token = _issue_email_token(db, user, "verify", timedelta(hours=s.email_verification_ttl_hours))
    link = f"{s.app_url}/verify-email?token={token}"
    get_mailer().send(
        db,
        user.email,
        "Verify your AURA account",
        f"Hi {user.display_name},\n\nConfirm your email: {link}\n\n"
        f"This link expires in {s.email_verification_ttl_hours} hours.",
    )


def signup(db: Session, email: str, password: str, display_name: str) -> None:
    email = normalize_email(email)
    validate_password(password, email)
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        # Same response as a new signup (no account enumeration); notify the real owner.
        get_mailer().send(
            db,
            email,
            "AURA sign-up attempt",
            "Someone tried to create an AURA account with this email. "
            "If this was you, sign in or reset your password instead.",
        )
        return
    user = User(
        email=email,
        password_hash=hash_password(password),
        display_name=display_name.strip()[:80] or email.split("@")[0],
    )
    db.add(user)
    db.flush()
    db.add(Workspace(owner_id=user.id, name="Personal"))
    audit(db, "user.signup", user)
    send_verification(db, user)


def verify_email(db: Session, token: str) -> User:
    user = _consume_email_token(db, token, "verify")
    if user.email_verified_at is None:
        user.email_verified_at = utcnow()
        admin_email = get_settings().bootstrap_admin_email
        if admin_email and normalize_email(admin_email) == user.email:
            user.role = "admin"
            audit(db, "user.bootstrap_admin", user)
        audit(db, "user.verified", user)
    return user


def resend_verification(db: Session, email: str) -> None:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is not None and user.email_verified_at is None:
        send_verification(db, user)


def login(db: Session, email: str, password: str, user_agent: str | None) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if not verify_password(user.password_hash if user else None, password) or user is None:
        raise AppError("invalid_credentials", GENERIC_LOGIN_ERROR, 401)
    if user.suspended_at is not None:
        raise AppError("account_suspended", "This account is suspended.", 403)
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
    token = new_token()
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=utcnow() + timedelta(hours=get_settings().session_ttl_hours),
            user_agent=(user_agent or "")[:255],
        )
    )
    audit(db, "user.login", user)
    return user, token


def session_user(db: Session, token: str) -> User | None:
    sess = db.scalar(select(AuthSession).where(AuthSession.token_hash == hash_token(token)))
    now = utcnow()
    if sess is None or sess.revoked_at is not None or _as_aware(sess.expires_at) < now:
        return None
    user = db.get(User, sess.user_id)
    if user is None or user.suspended_at is not None:
        return None
    if (now - _as_aware(sess.last_seen_at)).total_seconds() > 300:
        sess.last_seen_at = now
    return user


def logout(db: Session, token: str) -> None:
    db.execute(
        update(AuthSession)
        .where(AuthSession.token_hash == hash_token(token))
        .values(revoked_at=utcnow())
    )


def request_password_reset(db: Session, email: str) -> None:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None:
        return  # same response either way
    s = get_settings()
    token = _issue_email_token(db, user, "reset", timedelta(minutes=s.password_reset_ttl_minutes))
    get_mailer().send(
        db,
        user.email,
        "Reset your AURA password",
        f"Reset your password: {s.app_url}/reset-password?token={token}\n\n"
        f"This link expires in {s.password_reset_ttl_minutes} minutes and works once. "
        "If you did not ask for this, ignore this email.",
    )


def reset_password(db: Session, token: str, password: str) -> None:
    user = _consume_email_token(db, token, "reset")
    validate_password(password, user.email)
    user.password_hash = hash_password(password)
    # Changing the password signs out every existing session.
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    if user.email_verified_at is None:
        user.email_verified_at = utcnow()  # proving inbox access also verifies the email
    audit(db, "user.password_reset", user)
