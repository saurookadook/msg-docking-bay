# 0001 — How production images are built

- **Status:** Accepted (Option 2)
- **Date:** 2026-10-18, decided 2026-10-19

## Context

The local stack (`compose.yaml`) builds only `-dev` and `-test` stages, with the plain
install pattern of [ENV-17](../standards/docker-and-environment.md): copy the lockfile,
install, copy the source. Production images (`backend-prod`, `frontend-prod`, ENV-20 to
ENV-22) do not exist yet.

The repository now uses moon (`.moon/`), and the moon standard MDOCK-1 (in the shared
`agent-configs` standards, `docs/standards/moonrepo/docker-and-codegen.md`) says that in a moon workspace a
project's image is built from the workspace root with `moon docker scaffold` /
`moon docker setup`, replacing ENV-17's install mechanism.

Two facts complicate MDOCK-1 here:

- `frontend/` is its own pnpm root (its own `package.json`, `pnpm-workspace.yaml`, and
  lockfile), so the frontend image's context is `frontend/`, not the repository root as
  ENV-14 assumes. MDOCK-1 needs the repository root as the context.
- MDOCK-1's base stage installs proto and moon, which adds a network install and a second
  tool to every image build.

## Options

1. **MDOCK-1 for `-prod` stages.** Repository-root context, `-skeleton` stage, `moon docker
   scaffold <project>`, `moon docker setup`, `moon run <project>:build`, then the ENV-20
   or ENV-22 runtime stage. Builds exactly what `moon run` builds, and the scaffold keeps
   the dependency layer cached per project. Needs a root `.dockerignore` (ENV-16 plus
   MDOCK-3's `.moon/cache`) and a `docker-bake.hcl` that records the contexts (ENV-28).
2. **ENV-17 for every stage.** Extend the existing Dockerfiles with `-build` and `-prod`
   stages. No moon in images; the contexts stay `frontend/` and `backend/`. Diverges from
   MDOCK-1, and the image's build steps are a second description of what the moon `build`
   task does.

## Decision

**Option 2: ENV-17 for every stage.** `backend/Dockerfile` gains `backend-build` and
`backend-prod` (ENV-20, ENV-21), and `frontend/Dockerfile` gains `frontend-build` and
`frontend-prod` (Caddy, ENV-22), with the contexts still `backend/` and `frontend/`. A new
`postgres/Dockerfile` bakes `postgres/initdb/` into the pinned PostgreSQL image.
`docker-bake.hcl` records the three targets and their contexts (ENV-28), and
`scripts/publish-images.sh` pushes them (ENV-41; `moon run <project>:publish`).

## Consequences

- No moon or proto in any image, and no root `.dockerignore`.
- The image build steps (`pnpm build`, `uv sync --no-dev`) are a second description of
  what moon's `build` task does; keep them in step.
- `frontend-prod` copies `Caddyfile` and `/app/dist` from the `frontend/` context, not
  `frontend/Caddyfile` and `/repo/frontend/dist` as ENV-22's example has it.
