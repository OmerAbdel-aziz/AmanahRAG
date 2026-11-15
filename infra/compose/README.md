# compose

Local dependencies: PostgreSQL, Milvus (with etcd + MinIO), RabbitMQ, Keycloak.

```bash
cp .env.example .env
docker compose up -d                 # infrastructure only
docker compose --profile app up -d --build   # + api, web, gateway, worker
docker compose down                  # keep volumes
docker compose down -v               # wipe data
```

| Service        | URL                              | Notes                          |
| -------------- | -------------------------------- | ------------------------------ |
| PostgreSQL     | `localhost:5432`                 | user/db `amanah`               |
| Milvus         | `localhost:19530`                | gRPC, metrics on 9091          |
| MinIO          | `localhost:9000` (UI 9001)       | Milvus object storage          |
| RabbitMQ       | `localhost:5672` (UI 15672)      | user `amanah`                  |
| Keycloak       | `localhost:8080`                 | admin console, realm `amanah`  |

## Notes

- The first run has no database tables. After Postgres is healthy, apply the schema:
  `cd apps/api && npx prisma migrate dev --name init`. The first migration is intentionally
  not committed (see `apps/api/README.md`).
- Keycloak imports `keycloak/realm-export.json` on start: realm `amanah`, clients
  `amanah-web` (public, PKCE) and `amanah-api` (bearer-only). **No users are seeded**; create
  one in the admin console and grant the `user` role.
- Credentials in `.env.example` are local defaults. They are intentionally obvious; do not
  copy them to a shared environment.
- Milvus needs ~2 GB of memory. If it restarts in a loop, check `docker compose logs milvus`
  for the memory limit rather than raising retries.
- The app profile expects images to build from the repository root. Building `services/*`
  uses its own directory as context because those are standalone Python projects.
- Host ports are parameterised so several checkouts can run side by side.
