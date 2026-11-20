import logging
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.router import api_router
from app.api.v1.workflows import scheduler_loop
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.services.research import recover_stuck_runs

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
access = logging.getLogger("aura.access")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    recover_stuck_runs()  # in-process runs cannot survive a restart; mark them failed honestly
    stop = threading.Event()
    threading.Thread(target=scheduler_loop, args=(stop,), daemon=True, name="scheduler").start()
    yield
    stop.set()


def _init_monitoring(dsn: str) -> None:
    import sentry_sdk

    # No request bodies, cookies or user data are sent: messages and documents stay private.
    sentry_sdk.init(
        dsn=dsn,
        send_default_pii=False,
        max_request_body_size="never",
        traces_sample_rate=0.0,
        environment=get_settings().app_env,
    )


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.sentry_dsn:
        _init_monitoring(settings.sentry_dsn.get_secret_value())
    app = FastAPI(
        title="AURA API",
        lifespan=lifespan,
        version="0.1.0",
        docs_url=None if settings.is_production else "/api/docs",
        openapi_url=None if settings.is_production else "/api/openapi.json",
    )
    install_error_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["content-type", "x-csrf-token", "x-request-id"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        start = time.monotonic()
        response: Response = await call_next(request)
        # Access log: path only (no query string, bodies or cookies).
        access.info(
            "%s %s %s %dms rid=%s",
            request.method,
            request.url.path,
            response.status_code,
            (time.monotonic() - start) * 1000,
            getattr(request.state, "request_id", "-"),
        )
        for k, v in SECURITY_HEADERS.items():
            if k == "Content-Security-Policy" and request.url.path.startswith("/api/docs"):
                continue  # Swagger UI needs scripts; docs are disabled in production.
            response.headers.setdefault(k, v)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
