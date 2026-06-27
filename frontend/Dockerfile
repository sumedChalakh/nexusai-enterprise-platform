FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV BACKEND_URL=http://backend:8000
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app

RUN groupadd -r nextjs && useradd -r -g nextjs nextjs

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nextjs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nextjs /app/.next/static ./.next/static

USER nextjs

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', r => process.exit(r.statusCode === 200 ? 0 : 1))"

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]

# ── Dev stage (used by docker-compose override command: npm run dev) ──────────
FROM node:20-slim AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
CMD ["npm", "run", "dev"]
