# docs

| File             | Purpose                                            |
| ---------------- | -------------------------------------------------- |
| `architecture.md`| Components, request flow, trust boundaries, failure modes |
| `benchmark.md`   | Evaluation contract, ablations, targets            |
| `eval-report.md` | Latest results template (currently empty)          |
| `adr/`           | One decision per file, immutable once accepted     |

## ADR index

| #    | Decision                                             | Status   |
| ---- | ---------------------------------------------------- | -------- |
| 0001 | Record architecture decisions                        | accepted |
| 0002 | File bytes stay out of the control plane             | accepted |
| 0003 | Regex PII boundary now, NER later                    | accepted |

Open questions that need an ADR before production:

- Scrub-on-write for the vector store, or an access-controlled collection per tenant.
- Auth: Keycloak JWT guard in NestJS versus an API gateway in front of both services.
- Streaming answers without weakening citation checking.
