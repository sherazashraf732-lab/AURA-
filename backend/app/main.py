import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.services.research import recover_stuck_runs

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    recover_stuck_runs()  # in-process runs cannot survive a restart; mark them failed honestly
    yield


def create_app() -> FastAPI:
    settings = get_settings()
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
        response: Response = await call_next(request)
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
