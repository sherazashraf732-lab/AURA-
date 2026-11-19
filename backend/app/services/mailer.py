import logging
from typing import Protocol

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.identity import OutboxEmail

log = logging.getLogger("aura.mail")


class Mailer(Protocol):
    def send(self, db: Session, to: str, subject: str, body: str) -> None: ...


class OutboxMailer:
    """Development/test mailer: stores messages in the outbox table (viewable by admins in dev)."""

    def send(self, db: Session, to: str, subject: str, body: str) -> None:
        db.add(OutboxEmail(to_email=to, subject=subject, body=body))
        log.info(
            "email queued to outbox subject=%r", subject
        )  # never log the body (contains tokens)


class ResendMailer:
    """Resend HTTP API (free plan: 100 emails/day, 3,000/month, verified 2026-11-20)."""

    def __init__(self, api_key: str, sender: str) -> None:
        self.api_key, self.sender = api_key, sender

    def send(self, db: Session, to: str, subject: str, body: str) -> None:
        r = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"from": self.sender, "to": [to], "subject": subject, "text": body},
            timeout=10,
        )
        if r.status_code >= 400:
            log.error("resend send failed status=%s", r.status_code)
            raise RuntimeError("email delivery failed")


def get_mailer() -> Mailer:
    s = get_settings()
    if s.resend_api_key and s.mail_from:
        return ResendMailer(s.resend_api_key.get_secret_value(), s.mail_from)
    if s.is_production:
        raise RuntimeError("RESEND_API_KEY and MAIL_FROM are required in production")
    return OutboxMailer()
