"""Document -> chunks -> vectors. Kept free of RabbitMQ and Milvus clients so it unit-tests."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from worker.chunking import chunk_text, normalize_for_embedding
from worker.config import Settings
from worker.embeddings import Embedder
from worker.schemas import DocumentRef

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IngestResult:
    document_id: str
    chunks: int
    vectors: int


def process_document(
    document: DocumentRef, store, embedder: Embedder, settings: Settings
) -> IngestResult:
    chunks = chunk_text(document.text, settings.chunk_words, settings.chunk_overlap_words)
    if not chunks:
        logger.warning("document %s produced no chunks", document.id)
        return IngestResult(document_id=document.id, chunks=0, vectors=0)

    rows: list[dict] = []
    for batch_start in range(0, len(chunks), settings.embedding_batch_size):
        batch = chunks[batch_start : batch_start + settings.embedding_batch_size]
        texts = [normalize_for_embedding(chunk.text) for chunk in batch]
        vectors = embedder.embed(texts)
        if len(vectors) != len(batch):
            raise ValueError("embedder returned a different number of vectors than inputs")

        for chunk, vector in zip(batch, vectors, strict=True):
            chunk_id = f"{document.id}:{chunk.ordinal}"
            rows.append(
                {
                    "pk": str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)),
                    "chunk_id": chunk_id,
                    "document_id": document.id,
                    "title": document.title,
                    "language": document.language,
                    "ordinal": chunk.ordinal,
                    "text": chunk.text,
                    "source_uri": document.source_uri or "",
                    "embedding": vector,
                }
            )

    written = store.upsert(rows, document_id=document.id)
    logger.info("indexed document=%s chunks=%d", document.id, written)
    return IngestResult(document_id=document.id, chunks=len(chunks), vectors=written)
