from __future__ import annotations

import logging
import time
import uuid

from fastapi import APIRouter, Request

from app.config import get_settings
from app.graph import get_graph
from app.schemas import ChatRequest, ChatResponse, Citation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["chat"])

SNIPPET_CHARS = 320


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    settings = get_settings()
    started = time.perf_counter()
    trace_id = request.headers.get("x-request-id") or uuid.uuid4().hex

    mapping = getattr(request.state, "pii_mapping", {}) or {}
    top_k = payload.top_k or settings.top_k

    result = await get_graph().ainvoke(
        {
            "question": payload.question,
            "language": payload.language,
            "top_k": top_k,
            "pii_mapping": mapping,
        }
    )

    chunks = result.get("chunks", [])
    latency_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "trace=%s lang=%s chunks=%d model=%s latency_ms=%d",
        trace_id,
        payload.language,
        len(chunks),
        result.get("model", "unknown"),
        latency_ms,
    )

    return ChatResponse(
        trace_id=trace_id,
        answer=result.get("answer", ""),
        language=payload.language,
        model=result.get("model", "unknown"),
        latency_ms=latency_ms,
        citations=[
            Citation(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                snippet=" ".join(chunk.text.split())[:SNIPPET_CHARS],
                score=chunk.score,
            )
            for chunk in chunks
        ],
        pii_redactions=getattr(request.state, "pii_redactions", 0),
    )
