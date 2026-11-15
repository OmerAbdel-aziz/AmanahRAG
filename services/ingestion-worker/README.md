# ingestion-worker

Consumes `document.uploaded.v1`, chunks the text, embeds it and upserts vectors into Milvus.

```
event -> validate (pydantic) -> chunk (word windows + sentence snap) -> embed -> upsert
```

- `worker/consumer.py` — RabbitMQ topology, ack/nack, dead-letter queue.
- `worker/pipeline.py` — pure processing function; unit-tested without infrastructure.
- `worker/chunking.py` — Arabic normalisation for embeddings, original text preserved.
- `worker/embeddings.py` — BGE-M3 (lazy, optional) or a deterministic hash stand-in.
- `worker/milvus_store.py` — collection creation, delete-then-upsert per document.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m worker.main
```

## Configuration

| Variable               | Default                            |
| ---------------------- | ---------------------------------- |
| `RABBITMQ_URL`         | `amqp://amanah:amanah@localhost:5672/` |
| `QUEUE_NAME`           | `document.uploaded.v1`             |
| `MILVUS_URI`           | `http://localhost:19530`           |
| `MILVUS_COLLECTION`    | `amanah_chunks`                    |
| `EMBEDDING_BACKEND`    | `hash` (`bge-m3` needs `.[models]`) |
| `CHUNK_WORDS`          | `220`                              |
| `CHUNK_OVERLAP_WORDS`  | `40`                               |

## Notes

- The collection uses dynamic fields, so adding metadata does not require an ALTER.
- Failures reject without requeue and land in `document.uploaded.v1.dlq`. A malformed payload
  is a poison message; retrying it is worse than surfacing it.
- `process_document` is synchronous on purpose and called via `asyncio.to_thread`, because the
  Milvus SDK and FlagEmbedding are blocking.
