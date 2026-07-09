ARG NODE_BUILD_IMAGE
ARG NODE_RUN_IMAGE

# === Build Stage ==============================================================
FROM ${NODE_BUILD_IMAGE} AS builder

USER root

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

COPY package.json package-lock.json next.config.ts postcss.config.mjs tsconfig.json ./

RUN npm ci

COPY src ./src

RUN npm run build

# === Run Stage ==============================================================
FROM ${NODE_RUN_IMAGE} AS runner

USER root

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder --chown=1000:1000 /app/.next/standalone ./
COPY --from=builder --chown=1000:1000 /app/.next/static ./.next/static

USER 1000
EXPOSE 3000

ENTRYPOINT ["node"]
CMD ["server.js"]