"""Milvus writes.

The collection is created on first use with dynamic fields enabled, so metadata can grow
without a migration. The authoritative relational record stays in Postgres; if the two drift,
re-running ingestion for a document is safe because writes are upserts keyed by chunk id.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from worker.config import Settings

logger = logging.getLogger(__name__)


class MilvusStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    def _get_client(self):
        if self._client is None:
            from pymilvus import MilvusClient

            self._client = MilvusClient(uri=self.settings.milvus_uri)
        return self._client

    def ensure_collection(self) -> None:
        client = self._get_client()
        name = self.settings.milvus_collection
        if client.has_collection(name):
            return

        logger.info("creating Milvus collection %s", name)
        client.create_collection(
            collection_name=name,
            dimension=self.settings.embedding_dim,
            primary_field_name="pk",
            id_type="string",
            max_length=128,
            vector_field_name="embedding",
            metric_type="COSINE",
            auto_id=False,
            enable_dynamic_field=True,
        )

    def upsert(
        self, rows: list[dict[str, Any]], *, document_id: str, replace_document: bool = True
    ) -> int:
        if not rows:
            return 0
        client = self._get_client()
        self.ensure_collection()
        if replace_document:
            # Chunk counts shrink between runs; delete stale vectors first.
            client.delete(
                collection_name=self.settings.milvus_collection,
                filter=f"document_id == {json.dumps(document_id)}",
            )
        client.upsert(collection_name=self.settings.milvus_collection, data=rows)
        return len(rows)
