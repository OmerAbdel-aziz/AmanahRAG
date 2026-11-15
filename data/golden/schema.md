# Golden set schema

`questions.jsonl` — one JSON object per line, UTF-8, Arabic written right-to-left but stored
logically. Target size: **50–80 questions**, balanced across languages and difficulty.

| Field                   | Type             | Rules                                                        |
| ----------------------- | ---------------- | ------------------------------------------------------------ |
| `id`                    | string           | Stable, `{lang}-{topic}-{nn}`. Never reuse an id.            |
| `language`              | `ar` \| `en`     | Language of the question.                                    |
| `question`              | string           | What a user would actually type. No document names.          |
| `answerable`            | boolean          | False means the correct behaviour is a refusal.              |
| `expected_document_ids` | string[]         | Any of these counts as a retrieval hit. Empty when unanswerable. |
| `reference_answer`      | string \| null   | One acceptable answer, used for judging. Null when unanswerable. |
| `tags`                  | string[]         | Topic plus behavioural tags (`refusal`, `exception`, `renewal`). |
| `difficulty`            | easy \| medium \| hard | Hard = multi-constraint or requires combining sections. |

## Metrics

Retrieval is scored on the chunk's parent document. Generation is scored against
`reference_answer` and the returned citations.

| Metric                 | Definition                                             | Target  |
| ---------------------- | ------------------------------------------------------ | ------- |
| Recall@5               | share of answerable questions with a hit in the top 5  | ≥ 0.85  |
| MRR@10                 | mean reciprocal rank of the first hit                  | ≥ 0.70  |
| nDCG@10                | graded ranking quality                                 | ≥ 0.75  |
| Citation precision     | share of returned citations that support the answer    | ≥ 0.90  |
| Faithfulness           | answer claims supported by cited passages (LLM judge)  | ≥ 0.90  |
| Refusal accuracy       | unanswerable questions correctly refused               | 1.00    |
| PII leakage            | raw PII present in outbound model calls or logs        | 0       |
| p95 latency            | end-to-end `/v1/chat`                                  | < 4000 ms |

Always report Arabic and English separately as well as combined: a strong combined score can
hide a weak language.

## Adding a question

1. Write it against a document that exists in `data/synthetic/`.
2. Verify the reference answer by reading the source, not by asking the model.
3. Run `python scripts/eval.py --golden data/golden/questions.jsonl` (harness is a follow-up;
   see `docs/benchmark.md` for the intended interface).
