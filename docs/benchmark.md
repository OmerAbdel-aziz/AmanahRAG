# Benchmark and evaluation

> **Status:** harness not implemented. The interface and metric targets are fixed here so the
> corpus and the harness can be built against the same contract. No numbers have been
> published yet — `docs/eval-report.md` is intentionally empty of results.

## What is measured

Two separate questions, scored separately:

1. **Retrieval** — did the right document make it into the top-k context?
2. **Generation** — given those passages, is the answer correct, cited and honest about gaps?

Conflating them hides the common failure where the model is blamed for a missing passage.

## Data

- Corpus: `data/synthetic/` — paired Arabic/English policy documents.
- Questions: `data/golden/questions.jsonl` — see `data/golden/schema.md` for fields and
  metric definitions.

Every question carries `expected_document_ids` and, for answerable questions, a
`reference_answer` written by a human from the source document.

## Harness contract

`scripts/eval.py` (follow-up) should expose:

```bash
python scripts/eval.py \
  --golden data/golden/questions.jsonl \
  --gateway http://localhost:8000 \
  --top-k 5 \
  --out docs/eval-report.md
```

Rules:

- **Deterministic where possible.** `temperature=0`. Record the model id and git SHA in the
  report header; a score without them is not reproducible.
- **No judge without a rubric.** If an LLM judge is used for faithfulness, the rubric lives
  in the repo and the judge model is pinned. Human spot-checks of 10% of judged answers.
- **Report both languages.** Combined numbers hide a weak language.
- **Refusals are a first-class metric.** An answer to an unanswerable question is a failure,
  even if it sounds plausible.

## Ablations to run, in order

| # | Variable                        | Values                                  |
| - | ------------------------------- | --------------------------------------- |
| 1 | Chunk size / overlap            | 150/20, 220/40, 320/60 (words)          |
| 2 | `top_k`                         | 3, 5, 8                                 |
| 3 | Embedding model                 | hash (sanity floor), BGE-M3             |
| 4 | Language filter                 | on (same-language only), off (cross-lingual, needs pair de-duplication) |
| 5 | Reranker                        | none, cross-encoder on top 20           |
| 6 | Prompt                          | citation-mandating vs plain             |

Change one variable per run. Keep the raw per-question output next to the summary so a
regression can be traced to a specific question.

## Targets

From `data/golden/schema.md`: Recall@5 ≥ 0.85, MRR@10 ≥ 0.70, nDCG@10 ≥ 0.75, citation
precision ≥ 0.90, faithfulness ≥ 0.90, refusal accuracy 1.00, zero PII leakage, p95 < 4 s.

These are starting targets for a small, synthetic corpus. They are not claims about a
production system.

## Cost and time

The offline stub runs in seconds and tests wiring, not quality. A BGE-M3 ingest of 60 small
documents plus 80 generations on a hosted model is the realistic first benchmark: budget one
GPU-hour for embeddings and a few dollars for generation.
