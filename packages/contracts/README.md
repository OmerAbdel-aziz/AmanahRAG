# contracts

Single source of truth for the HTTP and event surface:

```
openapi/ai-gateway.yaml     POST /v1/chat, /healthz, /readyz
openapi/api.yaml            /api/documents, /api/health
events/*.v1.schema.json     RabbitMQ payloads (JSON Schema 2020-12)
src/index.ts                TypeScript mirror used by apps/web and apps/api
```

## Rules

- **Schemas change first.** A pull request that alters a request or event shape updates this
  package in the same commit as the producer and consumer.
- **Versioned events are append-only.** Breaking changes get `.v2`; never edit a `v1` schema
  in a way that rejects messages already in the dead-letter queue.
- **`additionalProperties: false`** on events. Unknown fields are a producer bug, not data.
- **No PII in events.** `query.answered.v1` exists for evaluation and must contain only
  redacted questions.

## Validate

```bash
npm run validate --workspace @amanah/contracts
```

The check is intentionally dependency-free: it parses every schema and asserts the event
invariants CI depends on. Full JSON Schema validation against fixtures is a follow-up.
