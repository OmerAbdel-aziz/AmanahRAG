# 0002 — File bytes stay out of the control plane

- **Status:** accepted
- **Date:** 2026-11-15
- **Deciders:** project maintainers

## Context

`POST /api/documents` accepts metadata, not a file. The ingestion worker needs the document
text, and the gateway only needs chunks in Milvus. Three options were on the table:

1. Upload bytes to the NestJS API, store them in Postgres.
2. Upload directly to object storage (S3-compatible) and publish a presigned reference.
3. Put the extracted text in the event payload (current skeleton).

Option 3 is what the worker contract assumes today. It is simple and keeps the pipeline
testable without a storage dependency, but it is wrong for large files and puts document text
on the message bus.

## Decision

For the skeleton, the event carries extracted text (option 3). Before any real deployment:

- add an S3-compatible bucket (`infra/compose` already runs MinIO for Milvus);
- upload via a presigned URL from the API;
- publish only `source_uri`, checksum and language in `document.uploaded.v1`;
- have the worker download, extract and delete its local copy.

The event schema is versioned, so this becomes `document.uploaded.v2` rather than an edit.
The ingestion worker's `DocumentRef.text` is therefore explicitly temporary.

## Consequences

- Local development needs no object storage today.
- RabbitMQ carries document text, which is a data-retention liability. Do not use this path
  with production documents.
- The API currently has no publishing code at all; the missing handoff is visible in
  `apps/api/README.md` rather than hidden behind a stub that silently discards events.

## Alternatives considered

- **Bytes in Postgres** — bloats backups and makes the API a file server.
- **Publish before the metadata commit** — risks an event for a row that rolled back.
