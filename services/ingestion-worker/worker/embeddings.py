"""Embedding backends.

``HashEmbedder`` is deterministic and dependency-free; the gateway implements the same
algorithm so a dev ingest is self-consistent. It is not semantic — use ``--backend bge-m3``
for anything resembling retrieval quality.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from worker.config import Settings


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def hash_embed(text: str, dim: int = 1024) -> list[float]:
    vector = [0.0] * dim
    for token in re.findall(r"\w+", text.lower()):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dim
        vector[index] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class HashEmbedder:
    def __init__(self, dim: int = 1024) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [hash_embed(text, self.dim) for text in texts]


class BGEM3Embedder:
    """BGE-M3 via FlagEmbedding. Lazy import keeps the base image small."""

    def __init__(self, model_name: str = "BAAI/bge-m3", dim: int = 1024) -> None:
        self.model_name = model_name
        self.dim = dim
        self._model = None

    def _load(self):
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel

            self._model = BGEM3FlagModel(self.model_name, use_fp16=True)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        output = self._load().encode(texts, batch_size=8, max_length=1024)["dense_vecs"]
        return [list(map(float, vector)) for vector in output]


def build_embedder(settings: Settings) -> Embedder:
    if settings.embedding_backend == "bge-m3":
        return BGEM3Embedder(settings.embedding_model, settings.embedding_dim)
    return HashEmbedder(settings.embedding_dim)
