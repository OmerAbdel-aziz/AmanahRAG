from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.middleware import PIIMiddleware
from app.routers.chat import router as chat_router
from app.schemas import HealthResponse

settings = get_settings()
logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title="Amanah AI Gateway",
    version=__version__,
    description="Bilingual RAG gateway. PII is redacted before any model call.",
)

# Middleware order: the last one added runs first, so CORS wraps the PII layer.
app.add_middleware(PIIMiddleware, enabled=settings.pii_redaction_enabled)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.web_origin.split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type", "x-request-id"],
)

app.include_router(chat_router)


@app.get("/healthz", response_model=HealthResponse, tags=["ops"])
async def healthz() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=__version__,
        environment=settings.environment,
        model=settings.litellm_model or "stub:extractive",
        retrieval_enabled=settings.milvus_enabled,
    )


@app.get("/readyz", tags=["ops"])
async def readyz() -> dict[str, str]:
    """Dependency readiness. Milvus and the model provider are checked lazily on first use,
    so this stays fast; wire real probes here before running this in production."""
    return {"status": "ready"}
