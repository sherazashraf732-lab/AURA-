from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables or backend/.env (never committed)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "AURA"
    app_url: str = "http://localhost:5173"
    api_base_url: str = "http://localhost:8000"
    secret_key: SecretStr = SecretStr("dev-only-insecure-secret-change-me")
    database_url: str = "postgresql+psycopg://aura:aura@127.0.0.1:5433/aura"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # Safety defaults (spec: no paid usage unless explicitly enabled by the owner).
    allow_paid_provider_usage: bool = False
    global_daily_spend_limit: float = 0
    default_user_daily_request_limit: int = 20
    max_upload_mb: int = 20
    max_concurrent_jobs_per_user: int = 2

    groq_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None
    mistral_api_key: SecretStr | None = None
    cloudflare_api_token: SecretStr | None = None
    cloudflare_account_id: str | None = None
    cerebras_api_key: SecretStr | None = None
    huggingface_api_key: SecretStr | None = None
    nvidia_api_key: SecretStr | None = None
    tavily_api_key: SecretStr | None = None
    exa_api_key: SecretStr | None = None
    # Shared free-tier protection: total AURA requests per provider per UTC day.
    provider_daily_request_cap: int = 500

    sentry_dsn: SecretStr | None = None  # optional error monitoring (Sentry free plan)

    resend_api_key: SecretStr | None = None
    mail_from: str | None = None
    bootstrap_admin_email: str | None = None  # first user with this email becomes admin

    session_ttl_hours: int = 24 * 7
    email_verification_ttl_hours: int = 24
    password_reset_ttl_minutes: int = 30

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.is_production and s.secret_key.get_secret_value().startswith("dev-only"):
        raise RuntimeError("SECRET_KEY must be set in production")
    return s
