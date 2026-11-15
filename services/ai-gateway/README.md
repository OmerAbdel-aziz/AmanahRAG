# ai-gateway

FastAPI service that answers questions from the indexed corpus. Responsibilities:

1. **PII boundary** — `app/middleware.py` scrubs JSON bodies before any handler runs and
   keeps the token map request-scoped (`app/pii.py`).
2. **Retrieval** — embeds the question and searches Milvus (`app/retrieval.py`).
3. **Orchestration** — a three-node LangGraph: retrieve → generate → restore (`app/graph.py`).
4. **Generation** — LiteLLM, or a deterministic extractive stub when no model is configured
   (`app/llm.py`).

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
pytest
```

## Configuration

| Variable                  | Default                  | Notes                                             |
| ------------------------- | ------------------------ | ------------------------------------------------- |
| `LITELLM_MODEL`           | *(empty)*                | Empty = offline stub. e.g. `openai/gpt-4o-mini`    |
| `LITELLM_EMBEDDING_MODEL` | *(empty)*                | Must match the worker's BGE-M3, e.g. `huggingface/BAAI/bge-m3` |
| `MILVUS_URI`              | `http://localhost:19530` |                                                   |
| `MILVUS_ENABLED`          | `true`                   | Set false to skip retrieval entirely              |
| `PII_REDACTION_ENABLED`   | `true`                   | Never disable outside a test                      |
| `PII_RESTORE_RESPONSE`    | `true`                   | Rehydrates tokens in the answer for the caller    |

## Deliberate limitations

- PII detection is regex-based (emails, IBAN, cards, phones, national IDs). Names and
  addresses need NER; that is ADR 0003's open question.
- Retrieval failures degrade to "no sources" rather than a 5xx. The UI surfaces an empty
  citation list, which is visible, not silent.
- `/readyz` does not probe Milvus yet.
- The hash embedder is a wiring tool, not a retrieval strategy.
