# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Crypto Service - Cryptocurrency Operations & AI/ML Integration."""

from __future__ import annotations

from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from crypto_service.routes import ai_router, alerts_router, prices_router
from shared.config import get_settings
from shared.database import ENGINE, TIMESCALE_ENGINE, health_check
from shared.exceptions import AppError, handle_exception
from shared.logger import init_logging, set_request_id
from shared.redis import get_redis_client
from shared.security import add_security_headers, apply_cors

settings = get_settings()
init_logging(settings.service_name, settings.log_level, settings.log_format == "json")

app = FastAPI(
    title="Wings of Capital - Crypto Service",
    description="Cryptocurrency operations & AI/ML pricing microservice",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

apply_cors(app)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    set_request_id(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return add_security_headers(response)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    http_exc = handle_exception(exc)
    return JSONResponse(status_code=http_exc.status_code, content=http_exc.detail)


app.include_router(prices_router)
app.include_router(alerts_router)
app.include_router(ai_router)


def _redis_health() -> bool:
    try:
        return bool(get_redis_client().ping())
    except Exception:
        return False


def _dependency_status() -> Dict[str, bool]:
    deps = {
        "database": health_check(ENGINE),
        "redis": _redis_health(),
    }
    if TIMESCALE_ENGINE is not None:
        deps["timescale"] = health_check(TIMESCALE_ENGINE)
    return deps


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    deps = _dependency_status()
    return {"status": "healthy", "service": settings.service_name, "dependencies": deps}


@app.get("/healthz/live")
async def liveness_probe():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@app.get("/healthz/ready")
async def readiness_probe(response: Response):
    """Kubernetes readiness probe."""
    deps = _dependency_status()
    is_ready = all(deps.values()) if deps else True
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if is_ready else "not_ready", "dependencies": deps}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
