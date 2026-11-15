FROM node:20-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json* ./
COPY apps/web/package.json apps/web/package.json
COPY apps/api/package.json apps/api/package.json
COPY packages/contracts/package.json packages/contracts/package.json
RUN npm ci --workspace @amanah/web --include-workspace-root

FROM node:20-alpine AS builder
WORKDIR /repo
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000
ARG NEXT_PUBLIC_API_URL=http://localhost:3001
ENV NEXT_PUBLIC_GATEWAY_URL=$NEXT_PUBLIC_GATEWAY_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
COPY --from=deps /repo/node_modules ./node_modules
COPY package.json ./
COPY apps/web ./apps/web
COPY packages/contracts ./packages/contracts
RUN npm run build --workspace @amanah/web

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
COPY --from=builder /repo/apps/web/.next/standalone ./
COPY --from=builder /repo/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /repo/apps/web/public ./apps/web/public
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
