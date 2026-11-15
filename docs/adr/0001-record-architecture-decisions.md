# 0001 — Record architecture decisions

- **Status:** accepted
- **Date:** 2026-11-15
- **Deciders:** project maintainers

## Context

The platform spans TypeScript and Python, four runtimes and three data stores. Decisions
about the PII boundary, chunking and evaluation will be revisited as the corpus grows, and the
reasoning is easy to lose in pull request threads.

## Decision

Keep short ADRs in `docs/adr/`, numbered, one decision each. An ADR is required when a change:

- alters a trust boundary (what leaves the process, what is stored);
- changes a wire format in `packages/contracts`;
- swaps a store, model family or orchestration framework;
- changes the evaluation methodology or a published target.

ADRs are immutable once accepted. A reversal adds a new ADR that supersedes the old one.

## Consequences

- Reviewers can judge a change against the recorded constraint, not memory.
- Slight overhead for small changes; the trigger list keeps it bounded.
- ADRs are prose, not tests. CI cannot enforce them, so review must.

## Alternatives considered

- **Design docs in the wiki** — drifts from the code and has no review trail.
- **Commit messages only** — too granular; the rationale for a boundary is not a commit.
