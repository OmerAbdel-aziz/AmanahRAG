# web

Next.js App Router UI for asking questions and reading cited answers.

- `app/page.tsx` — landing shell and copy.
- `components/ask-panel.tsx` — client component; posts to the AI gateway.
- `lib/api.ts` — typed gateway client. Keep the response type in sync with
  `packages/contracts/openapi/ai-gateway.yaml`.

## Environment

| Variable                   | Default                 |
| -------------------------- | ----------------------- |
| `NEXT_PUBLIC_GATEWAY_URL`  | `http://localhost:8000` |

## Run

From the repository root: `npm run dev:web` (or `npm install && npm run dev`).
