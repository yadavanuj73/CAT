"""
CAT Intelligence 2026 — FastAPI Application Entry Point.
Production-grade configuration with secret redaction, CORS,
exception filtering, and modular routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config import settings
from app.database import AsyncSessionLocal, engine, init_db
from app.routers import (
    analysis_router,
    api_keys_router,
    auth_router,
    mock_exams_router,
    papers_router,
    predictions_router,
    questions_router,
    shared_router,
)
from app.security.redaction import redact_secrets
from app.services.ingestion_service import recover_stalled_paper_extractions


import logging

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and recover any interrupted jobs from previous restart
    try:
        await init_db()
    except Exception as exc:
        logger.warning(f"init_db non-fatal warning during startup: {exc}")

    async with AsyncSessionLocal() as session:
        try:
            await recover_stalled_paper_extractions(session)
        except Exception:
            pass
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="CAT Intelligence 2026 API",
    description="Specialised AI-powered CAT examination intelligence platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware — sanitize wildcard origins so Chrome never blocks withCredentials requests
raw_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
clean_origins = [o.strip() for o in raw_origins if o.strip() and o.strip() != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=clean_origins,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler with strict secret redaction
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    raw_error = str(exc)
    safe_error = redact_secrets(raw_error)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "message": safe_error},
    )


# Health Check with live DB connectivity verification
@app.get("/api/health", tags=["Health"])
async def health_check():
    db_status = "disconnected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as exc:
        safe_err = redact_secrets(str(exc))
        logger.error(f"Health check DB failure: {safe_err}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "CAT Intelligence 2026 API",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "database": "disconnected",
                "detail": safe_err,
            },
        )

    is_sqlite_in_prod = (
        settings.ENVIRONMENT.lower() == "production"
        and engine.url.get_backend_name() == "sqlite"
    )
    return {
        "status": "degraded" if is_sqlite_in_prod else "healthy",
        "service": "CAT Intelligence 2026 API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "database_backend": engine.url.get_backend_name(),
    }


# Include Routers
app.include_router(auth_router, prefix="/api")
app.include_router(api_keys_router, prefix="/api")
app.include_router(papers_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
app.include_router(mock_exams_router, prefix="/api")
app.include_router(shared_router, prefix="/api")
