from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    language: Literal["ar", "en"] = "en"
    top_k: int | None = Field(default=None, ge=1, le=20)


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    trace_id: str
    answer: str
    language: Literal["ar", "en"]
    model: str
    latency_ms: int
    citations: list[Citation] = Field(default_factory=list)
    pii_redactions: int = 0


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    version: str
    environment: str
    model: str
    retrieval_enabled: bool
