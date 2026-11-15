# data

Evaluation data for the bilingual assistant. Everything here is **synthetic**: no real
donor, volunteer or staff data. Do not add production documents.

```
synthetic/
  en/    English source documents
  ar/    Arabic counterparts, same pair_id
golden/
  questions.jsonl   evaluation questions
  schema.md         field definitions and metric targets
```

## Synthetic corpus

The seed set is three bilingual policy pairs (6 documents): records retention, refunds and
expense approvals, volunteer onboarding. They are deliberately short and number-dense so
retrieval and citation behaviour can be checked by hand.

Target for the full corpus is **30 Arabic + 30 English documents**, organised as 30 pairs.
Each document carries front matter:

```yaml
doc_id: en-retention-001      # {lang}-{topic}-{nnn}
pair_id: retention-policy      # same value in both languages
title: Records retention policy
language: en
source: synthetic
status: sample                 # sample | reviewed | frozen
effective: 2026-01-01
```

Rules for growing the set:

- One topic per document, 300–900 words, with concrete numbers and at least one exception.
- Arabic is written first for Arabic-origin topics, then translated; do not machine-translate
  both directions or the pair stops testing cross-lingual retrieval.
- Every number in a document must be consistent with its pair.
- Freeze documents only after a second reader checks the facts.

## Why pairs

Paired documents make it possible to separate two failures: the retriever missing a passage
(retrieval) versus the model ignoring a passage it received (generation). They also make
translation drift visible: if the Arabic and English answers disagree, one document is wrong.

Retrieval currently filters by the question's language, so a question never crosses over to
its paired document. That avoids returning two near-identical translations for every query,
but it means multilingual retrieval is not exercised by default. Lifting the filter requires
de-duplicating by `pair_id`; that is an ablation in `docs/benchmark.md`, not a default.

## Status

| Item                  | State                          |
| --------------------- | ------------------------------ |
| Synthetic documents   | 6 of 60 (format examples)      |
| Golden questions      | 10 of 50–80                    |
| Eval harness          | not implemented — `docs/benchmark.md` |
