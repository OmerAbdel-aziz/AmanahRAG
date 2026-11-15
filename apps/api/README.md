# api

NestJS control plane: document metadata, ingestion job tracking and feedback. It owns
PostgreSQL through Prisma and never talks to Milvus directly.

## Endpoints (prefix `/api`)

| Method | Path              | Purpose                       |
| ------ | ----------------- | ----------------------------- |
| GET    | `/health`         | Liveness plus database check  |
| GET    | `/documents`      | Recent documents with counts  |
| GET    | `/documents/:id`  | Document, chunks count, jobs  |
| POST   | `/documents`      | Register document metadata    |

## Database

```bash
npm run db:generate --workspace @amanah/api
npm run db:migrate  --workspace @amanah/api -- --name init
```

The first migration is intentionally not committed: Prisma writes it after the database is
reachable, and the CI job only runs `prisma generate` + `tsc`.

## Known gaps

- File bytes are not stored yet (no object storage decision — see `docs/adr/0002`).
- `document.uploaded.v1` is not published yet; the event schema exists in
  `packages/contracts/events/`.
- Auth is not enforced on routes; Keycloak is provisioned in compose but the JWT guard is a
  follow-up.
