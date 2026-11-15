# 0003 — Regex PII boundary now, NER later

- **Status:** accepted
- **Date:** 2026-11-15
- **Deciders:** project maintainers

## Context

The assistant handles donor and volunteer questions. Prompts must not carry raw personal data
to a third-party model provider. Detection options:

1. Presidio plus a spaCy Arabic model (NER for names, addresses, organisations).
2. A hosted DLP service.
3. Hand-written regexes for structured identifiers.

Option 1 is the most complete, but Arabic NER quality varies, the image grows by hundreds of
megabytes, and false positives on Arabic names are common enough to make answers incoherent.
Option 2 adds a network dependency on the critical path and a second data processor.

## Decision

Ship regex-based redaction for structured identifiers: email, IBAN, card-like digit runs,
phone numbers and national IDs. Detection happens in ASGI middleware before routing, so the
boundary is one file and cannot be bypassed by a new endpoint. Tokens are request-scoped and
restored only in the response to the original caller.

Unstructured PII (names, addresses) is **not** redacted. Two mitigations apply:

- The prompt instructs the model to answer from passages and refuse out-of-scope questions.
- The system prompt path only ever receives the user's question and retrieved chunks, not a
  user profile.

This ADR must be revisited before handling production data. Presidio is the expected upgrade,
gated behind a feature flag so the regex layer remains the deterministic floor.

## Consequences

- Fast, dependency-free, auditable, and easy to unit test.
- Arabic-Indic digits and dialectal spellings need explicit patterns; some false positives
  (dates, long reference numbers) are accepted.
- Names still leak to the model provider. That is a known, documented gap, not an oversight.
- The vector store contains unredacted chunk text. ADR 0002's storage work should include a
  decision on scrub-on-write.

## Alternatives considered

- **Presidio now** — better recall, worse latency and a large attack surface for a skeleton.
- **No redaction, rely on provider policy** — unacceptable for the stated trust boundary.
