# Amanah RAG (lite)

[![ci](https://github.com/OmerAbdel-aziz/AmanahRAG/actions/workflows/ci.yml/badge.svg)](https://github.com/OmerAbdel-aziz/AmanahRAG/actions/workflows/ci.yml)

A bilingual (Arabic / English) retrieval-augmented generation stack with a strict PII boundary,
citation-first answers, and an offline-friendly evaluation loop.

> **Status:** skeleton. The wiring, contracts and local infrastructure are in place; the
> retrieval quality work (corpus, golden set, tuning) is tracked in `docs/benchmark.md`.

## Layout

```
apps/
  web/                Next.js + React UI
  api/                NestJS + Prisma control plane (documents, jobs, feedback)
services/
  ai-gateway/         FastAPI + LangGraph + LiteLLM + PII middleware
  ingestion-worker/   RabbitMQ consumer, chunking, BGE-M3 embeddings, Milvus writer
packages/
  contracts/          Shared OpenAPI + event schemas + TypeScript types
data/
  synthetic/          30 Arabic + 30 English source documents
  golden/             50-80 evaluation questions
infra/
  compose/            Postgres, Milvus, RabbitMQ, Keycloak
docs/                 Architecture, ADRs, benchmark and eval reports
```

## Data flow

1. An operator uploads a document through `apps/api`.
2. The API stores metadata in Postgres and publishes `document.uploaded.v1` to RabbitMQ.
3. `services/ingestion-worker` normalises text, chunks it, embeds with BGE-M3 and writes
   vectors to Milvus.
4. `apps/web` asks `services/ai-gateway` a question.
5. The gateway redacts PII, retrieves chunks from Milvus, generates a grounded answer with
   LiteLLM, and restores the caller's own PII in the response only.

See `docs/architecture.md` for the component view and `docs/adr/` for the trade-offs.

## Quick start

Prerequisites: Node.js 20+, Python 3.11+, Docker with Compose v2.

```bash
# 1. Local infrastructure (Postgres, Milvus, RabbitMQ, Keycloak)
cp infra/compose/.env.example infra/compose/.env
docker compose -f infra/compose/docker-compose.yml up -d

# 2. Control plane + UI
npm install
npm run db:generate
npm run dev

# 3. AI gateway
cd services/ai-gateway
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

The gateway runs without an LLM key: it returns a deterministic stub answer so the graph,
retrieval and PII paths stay testable offline. Set `LITELLM_MODEL` and the matching provider
key to use a real model.

### Ports

| Service         | Port  |
| --------------- | ----- |
| web             | 3000  |
| api             | 3001  |
| ai-gateway      | 8000  |
| postgres        | 5432  |
| milvus          | 19530 |
| rabbitmq        | 5672 (UI 15672) |
| keycloak        | 8080  |

## Contracts

`packages/contracts` is the single source of truth for the HTTP and event surface. Change a
schema there first, then regenerate or update the consumers. CI validates that the OpenAPI
document parses and that event schemas declare `additionalProperties: false`.

## Not built yet

The skeleton is honest about its edges:

- **Corpus and golden set are seeds, not a benchmark.** 6 of 60 documents and 10 of 50–80
  questions exist; see `data/README.md` for the expansion rules.
- **No evaluation harness.** The interface and targets are fixed in `docs/benchmark.md`.
- **The API does not publish events yet.** Metadata is stored; the RabbitMQ handoff is a
  follow-up (ADR 0002).
- **No auth guard.** Keycloak is provisioned in compose, but routes are open.
- **No reranker or streaming.** Baseline retrieval only (`top_k=5`, one embedding model).

## Testing

```bash
npm test                  # api unit tests
npm run validate:contracts
cd services/ai-gateway && pytest
cd services/ingestion-worker && pytest
```

Evaluation is separate from unit tests: see `docs/benchmark.md` for the harness contract and
`docs/eval-report.md` for the latest numbers.
