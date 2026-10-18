# syntax=docker/dockerfile:1
# check=error=true

# Development and test stages only. How production images are built is an open
# decision: docs/decisions/0001-production-image-build.md.
#
# The build context is frontend/, which is the pnpm root (it has its own package.json,
# pnpm-workspace.yaml, and lockfile), not the repository root as ENV-14 describes.

ARG NODE_IMAGE=node:24.22.0-bookworm@sha256:14078204b6bb268c107ceff6d3c43f45a888105e5c2b18b14c32b3409d93a1b0

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

FROM frontend-base AS frontend-dev
EXPOSE 5173
ENTRYPOINT ["pnpm"]
CMD ["start:dev"]

FROM frontend-base AS frontend-test
ENTRYPOINT ["pnpm"]
CMD ["test"]
