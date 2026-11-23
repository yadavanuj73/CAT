"""
CAT Intelligence 2026 — FastAPI Application Entry Point.
Production-grade configuration with secret redaction, CORS,
exception filtering, and modular routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import AsyncSessionLocal, init_db
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and recover any interrupted jobs from previous restart
    await init_db()
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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


# Health Check
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "CAT Intelligence 2026 API",
        "version": "1.0.0",
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
