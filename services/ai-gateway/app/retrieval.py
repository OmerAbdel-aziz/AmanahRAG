"""Retrieval from Milvus.

Two embedders are available:

* ``LiteLLMEmbedder`` — calls the same embedding model the ingestion worker uses. This is
  the production path.
* ``HashEmbedder`` — deterministic, dependency-free, semantically meaningless. It exists so
  the graph and the UI can be exercised without model downloads. Both services implement the
  same algorithm so a locally ingested corpus is at least self-consistent.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import math
import re
from dataclasses import dataclass
from typing import Protocol

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RetrievedChunk:
    document_id: str
    chunk_id: str
    title: str
    text: str
    score: float
    language: str = "en"


class Embedder(Protocol):
    async def embed_query(self, text: str) -> list[float]: ...


def hash_embed(text: str, dim: int = 1024) -> list[float]:
    vector = [0.0] * dim
    for token in re.findall(r"\w+", text.lower()):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dim
        vector[index] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class HashEmbedder:
    def __init__(self, dim: int) -> None:
        self.dim = dim

    async def embed_query(self, text: str) -> list[float]:
        return hash_embed(text, self.dim)


class LiteLLMEmbedder:
    def __init__(self, model: str, dim: int) -> None:
        self.model = model
        self.dim = dim

    async def embed_query(self, text: str) -> list[float]:
        import litellm

        response = await litellm.aembedding(model=self.model, input=[text])
        vector = list(response.data[0]["embedding"])
        if len(vector) != self.dim:
            raise ValueError(
                f"embedding dimension mismatch: model returned {len(vector)}, expected {self.dim}"
            )
        return vector


class Retriever(Protocol):
    async def retrieve(
        self, query: str, language: str, top_k: int
    ) -> list[RetrievedChunk]: ...


class NullRetriever:
    async def retrieve(self, query: str, language: str, top_k: int) -> list[RetrievedChunk]:
        return []


class MilvusRetriever:
    def __init__(self, settings: Settings, embedder: Embedder) -> None:
        self.settings = settings
        self.embedder = embedder
        self._client = None

    def _get_client(self):
        if self._client is None:
            from pymilvus import MilvusClient

            self._client = MilvusClient(uri=self.settings.milvus_uri)
        return self._client

    async def retrieve(
        self, query: str, language: str, top_k: int
    ) -> list[RetrievedChunk]:
        try:
            vector = await self.embedder.embed_query(query)
            hits = await asyncio.to_thread(self._search, vector, language, top_k)
        except Exception as error:  # noqa: BLE001 - retrieval degrades, chat still answers
            logger.warning("milvus retrieval failed: %s", error)
            return []

        return [
            RetrievedChunk(
                document_id=str(hit["entity"].get("document_id", "")),
                chunk_id=str(hit["entity"].get("chunk_id", hit.get("id", ""))),
                title=str(hit["entity"].get("title", "Untitled")),
                text=str(hit["entity"].get("text", "")),
                score=float(hit.get("distance", 0.0)),
                language=str(hit["entity"].get("language", language)),
            )
            for hit in hits
        ]

    def _search(self, vector: list[float], language: str, top_k: int) -> list[dict]:
        client = self._get_client()
        return client.search(
            collection_name=self.settings.milvus_collection,
            data=[vector],
            limit=top_k,
            filter=f'language == "{language}"',
            output_fields=["document_id", "chunk_id", "title", "text", "language"],
            search_params={"metric_type": "COSINE", "params": {}},
        )[0]


class _RetrieverHolder:
    instance: Retriever | None = None


def get_retriever() -> Retriever:
    if _RetrieverHolder.instance is None:
        settings = get_settings()
        if not settings.milvus_enabled:
            _RetrieverHolder.instance = NullRetriever()
        else:
            embedder: Embedder
            if settings.litellm_embedding_model:
                embedder = LiteLLMEmbedder(
                    settings.litellm_embedding_model, settings.embedding_dim
                )
            else:
                logger.warning("no LITELLM_EMBEDDING_MODEL set; using the offline hash embedder")
                embedder = HashEmbedder(settings.embedding_dim)
            _RetrieverHolder.instance = MilvusRetriever(settings, embedder)
    return _RetrieverHolder.instance


def reset_retriever() -> None:
    """Test helper: drop the cached retriever."""
    _RetrieverHolder.instance = None
