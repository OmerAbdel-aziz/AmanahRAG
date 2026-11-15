# Evaluation report

> **No results yet.** This file is a template. The first run happens after the corpus reaches
> 30 + 30 documents and the harness described in `docs/benchmark.md` exists.
>
> Publishing invented numbers here would be worse than an empty report: it would make the
> project look finished while hiding whether retrieval works.

## Run header (fill on every run)

| Field            | Value |
| ---------------- | ----- |
| Date             | —     |
| Git SHA          | —     |
| Corpus           | —     |
| Questions        | —     |
| Embedding model  | —     |
| Generation model | —     |
| `top_k`          | —     |
| Chunk words/overlap | —  |

## Summary

| Metric            | Arabic | English | Combined | Target |
| ----------------- | ------ | ------- | -------- | ------ |
| Recall@5          | —      | —       | —        | ≥ 0.85 |
| MRR@10            | —      | —       | —        | ≥ 0.70 |
| nDCG@10           | —      | —       | —        | ≥ 0.75 |
| Citation precision| —      | —       | —        | ≥ 0.90 |
| Faithfulness      | —      | —       | —        | ≥ 0.90 |
| Refusal accuracy  | —      | —       | —        | 1.00   |
| PII leakage       | —      | —       | —        | 0      |
| p95 latency (ms)  | —      | —       | —        | < 4000 |

## Failures worth reading

Group by cause, not by question id:

- **Retrieval miss** — expected document absent from top-k. Include the query, the ranked
  document ids and whether the paired-language document was retrieved instead.
- **Generation drift** — passage retrieved, answer contradicts it.
- **Unsupported citation** — `[n]` points to a passage that does not contain the claim.
- **False refusal** — answerable question refused.
- **Leak** — any raw PII in a prompt, log or response. Severity: blocker.

## Decision log

Record what changes as a result: chunk size, prompt, `top_k`, reranker, corpus fix. Link the
ADR if a trust boundary moves.
