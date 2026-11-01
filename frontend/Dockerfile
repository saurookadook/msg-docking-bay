# syntax=docker/dockerfile:1
# check=error=true

# Production stages follow ENV-17, not moon's MDOCK-1:
# docs/decisions/0001-production-image-build.md.
#
# The build context is frontend/, which is the pnpm root (it has its own package.json,
# pnpm-workspace.yaml, and lockfile), not the repository root as ENV-14 describes.

ARG NODE_IMAGE=node:24.22.0-bookworm@sha256:14078204b6bb268c107ceff6d3c43f45a888105e5c2b18b14c32b3409d93a1b0
ARG CADDY_IMAGE=caddy:2.11.7-alpine@sha256:d8542f48d34a9cf4e4c11a478865229840e87e4c96ea3f439101f31a5d35f75f

FROM ${NODE_IMAGE} AS frontend-base
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    PNPM_HOME=/pnpm \
    npm_config_store_dir=/pnpm/store
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable
WORKDIR /app
# package.json for its `packageManager` pin; pnpm-workspace.yaml for pnpm's settings.
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store pnpm fetch
COPY . .
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --offline --frozen-lockfile

FROM frontend-base AS frontend-build
RUN pnpm build

FROM frontend-base AS frontend-dev
EXPOSE 5173
ENTRYPOINT ["pnpm"]
CMD ["start:dev"]

FROM frontend-base AS frontend-test
ENTRYPOINT ["pnpm"]
CMD ["test"]

FROM ${CADDY_IMAGE} AS frontend-prod
RUN addgroup -S app && adduser -S -G app app
# admin, persist_config, and auto_https are off, so Caddy writes nothing that matters here.
ENV XDG_CONFIG_HOME=/tmp/caddy-config XDG_DATA_HOME=/tmp/caddy-data
WORKDIR /srv
COPY Caddyfile ./Caddyfile
RUN caddy validate --config Caddyfile --adapter caddyfile
COPY --from=frontend-build /app/dist ./dist
USER app
EXPOSE 8080
CMD ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]
