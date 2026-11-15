from __future__ import annotations

import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from worker.config import Settings
from worker.embeddings import Embedder
from worker.pipeline import process_document
from worker.schemas import DocumentUploadedV1

logger = logging.getLogger(__name__)


class IngestionConsumer:
    def __init__(self, settings: Settings, store, embedder: Embedder) -> None:
        self.settings = settings
        self.store = store
        self.embedder = embedder
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    async def run(self) -> None:
        self._connection = await aio_pika.connect_robust(self.settings.rabbitmq_url)
        async with self._connection:
            channel = await self._connection.channel()
            await channel.set_qos(prefetch_count=self.settings.prefetch_count)

            exchange = await channel.declare_exchange(
                self.settings.dead_letter_exchange, aio_pika.ExchangeType.FANOUT, durable=True
            )
            dead_letter = await channel.declare_queue(
                f"{self.settings.queue_name}.dlq", durable=True
            )
            await dead_letter.bind(exchange)

            queue = await channel.declare_queue(
                self.settings.queue_name,
                durable=True,
                arguments={"x-dead-letter-exchange": self.settings.dead_letter_exchange},
            )
            await queue.consume(self._handle)
            logger.info("consuming %s", self.settings.queue_name)
            await asyncio.Event().wait()

    async def _handle(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False, reject_on_redelivered=False):
            try:
                payload = json.loads(message.body)
                event = DocumentUploadedV1.model_validate(payload)
            except Exception as error:  # noqa: BLE001 - malformed events must not loop
                logger.error("rejecting malformed event: %s", error)
                raise

            # Blocking work (model + Milvus SDK) runs off the event loop.
            result = await asyncio.to_thread(
                process_document, event.document, self.store, self.embedder, self.settings
            )
            logger.info(
                "ack document=%s chunks=%d vectors=%d",
                result.document_id,
                result.chunks,
                result.vectors,
            )
