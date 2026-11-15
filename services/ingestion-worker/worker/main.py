from __future__ import annotations

import asyncio
import logging

from worker.config import get_settings
from worker.consumer import IngestionConsumer
from worker.embeddings import build_embedder
from worker.milvus_store import MilvusStore


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    logger = logging.getLogger("worker")

    store = MilvusStore(settings)
    embedder = build_embedder(settings)
    logger.info(
        "starting worker backend=%s collection=%s",
        settings.embedding_backend,
        settings.milvus_collection,
    )

    consumer = IngestionConsumer(settings, store, embedder)
    try:
        await consumer.run()
    except asyncio.CancelledError:
        logger.info("worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
