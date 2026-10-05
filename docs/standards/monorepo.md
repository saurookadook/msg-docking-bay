# Monorepo Standards

Applies to repository structure, workspace boundaries, the `shared` package, root
scripts, and the API contract between the Python backend and the TypeScript frontend.

---

## Workspaces

**MONO-1 — The repository holds a pnpm workspace for the TypeScript code and a uv project
for the backend:**

```txt
<repo>/
  frontend/   @app/frontend React UI                                (pnpm workspace)
  shared/     @app/shared   API contract types + framework-free code (pnpm workspace)
  backend/                  FastAPI service                          (uv project, python/)
  package.json              root scripts, shared tooling, packageManager
  pnpm-workspace.yaml       workspace packages and pnpm settings
  pnpm-lock.yaml
  tsconfig.json             project references only
  compose.yaml
```

Workspace packages are listed in `pnpm-workspace.yaml`, not in a `workspaces` field in
`package.json`. `backend` is not a pnpm workspace: it has no `package.json`, and its
dependencies, lockfile (`backend/uv.lock`), and tool configuration live in
`backend/pyproject.toml` ([python/python.md](python/python.md) PY-2, PY-9).

```yaml
packages:
  - frontend
  - shared
onlyBuiltDependencies:
  - esbuild
```

Package names share one scope: `@app/frontend`, `@app/shared`.

**MONO-2 — Depend on sibling workspaces with `"workspace:*"`.** Never import across
workspaces with relative paths (`../../shared/src/...`); import the package by name.

**MONO-3 — Dependencies flow one way:** `frontend → shared`, and the API contract flows
`backend → shared` through generated files (MONO-13). `shared` MUST NOT import from
`frontend`. The backend imports nothing from `frontend` or `shared`, and no TypeScript
code reads files under `backend/`.

---

## The `shared` package

**MONO-4 — Put code in `shared` when it defines the contract with the backend, or when it
is framework-free and reusable:**

- the API contract generated from the backend: `shared/openapi/openapi.json` and the
  TypeScript types in `shared/src/generated/` (MONO-13), with named aliases (MONO-15)
- the WebSocket event-name constants, checked against the generated message types
  ([websockets.md](websockets.md))
- validation patterns used by forms, checked against the schema (MONO-16)
- pure domain logic the frontend needs that the API does not return (display rules,
  calculations), and constants and types that are not part of the API
- the logger (`sharedLog`) and small utilities (`safeParseJSON`, `deeplyMerge`, `isUUID`)
- test matchers, fixtures, and state generators (in the testing entry point; see MONO-7)

**MONO-5 — `shared` stays framework-free and environment-agnostic.** Its runtime code uses
no React, DOM-only APIs, or Node-only APIs ([nodejs.md](nodejs.md) NODE-7), so it can run
in the browser, in Vitest, and in Jest. Its runtime `dependencies` list only what that
code imports; the generated types need none.

**MONO-6 — `shared/src/index.ts` is the package's only runtime entry point.** Every export
that consumers rely on goes through it. Re-export type-only modules with
`export type * from './types'`.

**MONO-7 — Export test-only code from a separate `@app/shared/testing` entry point**
(declared in the `exports` map), so production bundles never include matchers, fixtures,
or generators.

**MONO-8 — Build `shared` with tsup to ESM (`dist`), with type declarations**, and
describe the output in the `exports` map in its `package.json`. Its only consumer is the
Vite frontend, so it emits no CommonJS. After changing `shared`, rebuild it
(`pnpm shared:base build`) before running or testing the frontend. The frontend's
Dockerfile builds `shared` first.

**MONO-9 — Do not duplicate a definition that already exists in `shared`.** If the
frontend needs a variant, extend the shared type locally
(`type ProjectCard = Pick<Project, 'project_id' | 'name'> & { ... }`). Never hand-write a
type for an API request or response; use the generated one (MONO-13).

**MONO-10 — Keep framework versions aligned across workspaces.** Any package used by more
than one workspace (`typescript`, test runners) MUST resolve to the same major
everywhere. Use a pnpm `catalog` in `pnpm-workspace.yaml` to pin shared versions in one
place.

---

## Root scripts

**MONO-11 — The root `package.json` exposes per-workspace scripts with a consistent
prefix**, and wraps the backend's uv and Compose commands so the whole repository is
driven from the root:

| Script            | Purpose                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `<pkg>:base`      | `pnpm --filter @app/<pkg>`: runs any script in that workspace (`frontend`, `shared`)          |
| `<pkg>:test`      | runs that workspace's tests                                                                   |
| `all:<task>`      | runs a task in every pnpm workspace in dependency order (`pnpm -r run <task>`)                |
| `dcr`             | `docker compose run --rm --remove-orphans`                                                    |
| `backend:run`     | `docker compose run --rm backend`, followed by any command (`pnpm backend:run alembic heads`) |
| `backend:check`   | the PY-8 and PY-50 commands, in CI's order, with `uv --directory backend run ...`             |
| `backend:test`    | the test Compose project, as CI runs it ([docker-and-environment.md](docker-and-environment.md) ENV-4) |
| `backend:migrate` | `docker compose run --rm backend-migrations upgrade head` (ALEM-13)                           |
| `api:generate`    | regenerates the API contract in `shared` (MONO-13)                                            |
| `docker:publish`  | the laptop fallback for publishing images when CI cannot ([docker-and-environment.md](docker-and-environment.md) ENV-41) |

Add a root alias for a workspace script that is run often; otherwise use
`pnpm <pkg>:base <script>`, or `uv run <command>` inside `backend/`.

- `pnpm -r` runs workspaces in dependency order, so `shared` builds first.
- Long-running watchers (`all:start:dev`) need `pnpm -r --parallel run start:dev`, since
  each watcher never exits.
- To run a task for one workspace plus the workspaces it depends on, use
  `pnpm --filter "@app/frontend..." build`.

**MONO-12 — Every pnpm workspace defines `build`, `test`, and `typecheck` scripts**, and
the frontend also defines `start:dev`. Workspaces whose tests run on the CI runner also
define `test:cov` ([ci-pipeline.md](ci-pipeline.md) CI-2). Formatting and linting of
TypeScript, JSON, CSS, and Markdown are root-only scripts (`format`, `format:check`,
`lint`, `lint:fix`) that cover every workspace
([formatting-and-linting.md](formatting-and-linting.md) FMT-11); workspaces do not define
their own. The backend's equivalents are its `uv run` commands (PY-8, PYTEST-3), wrapped
by the `backend:*` scripts above. A script that needs an environment file loads it from
the root rather than keeping a separate copy.

---

## The API contract

**MONO-13 — The backend's OpenAPI schema is the API contract, and the TypeScript types for
it are generated, never hand-written.** `pnpm api:generate` runs three steps, and its
output is committed:

1. `uv --directory backend run python -m scripts.export_openapi` writes
   `app.openapi()` to `shared/openapi/openapi.json`, with sorted keys. It imports the app
   without starting a server or touching the database (the engine is built on first use,
   SQLA-14), so it runs anywhere the backend's environment is installed.
2. `openapi-typescript` turns that file into `shared/src/generated/api.ts` (types only, no
   runtime code).
3. oxfmt formats both files, so the committed output is exactly what the generator and
   formatter produce, and the CI drift check (MONO-14) compares like with like.

Pydantic models, route signatures, and route docstrings (FAPI-7, FAPI-15) are therefore
the single definition of every request, response, and error shape. Field names stay as
the backend defines them, `snake_case` ([python/fastapi.md](python/fastapi.md) FAPI-12):
the frontend uses them as generated, with no renaming or mapping layer
([typescript.md](typescript.md) TS-4).

**MONO-14 — Regenerate the contract in the same PR that changes it.** Any change to a
route, a request or response model, an entity a response contains, or a WebSocket message
model (MONO-17) is followed by `pnpm api:generate`, and the generated diff is committed
with it. CI regenerates the contract and fails if anything differs
([ci-pipeline.md](ci-pipeline.md) CI-9). Never edit `shared/openapi/` or
`shared/src/generated/` by hand; oxlint ignores the generated directory
([formatting-and-linting.md](formatting-and-linting.md) FMT-11).

**MONO-15 — Expose the generated types through named aliases.** `shared/src/api/index.ts`
re-exports each schema the frontend uses under its model's name, and the frontend imports
those aliases from `@app/shared`, never `components['schemas'][...]` directly:

```ts
import type { components } from '../generated/api';

type Schemas = components['schemas'];

export type Project = Schemas['ProjectEntity'];
export type ProjectResponse = Schemas['ProjectResponse'];
export type ProjectsListResponse = Schemas['ProjectsListResponse'];
export type ProjectCreateRequest = Schemas['ProjectCreateRequest'];
```

When a backend model is renamed, the alias is the one line that changes, and the
frontend's typecheck shows every use that needs attention.

**MONO-16 — A validation rule that both the frontend and the backend enforce is defined
in the backend and checked in `shared`.** The Pydantic field (`Field(pattern=...,
min_length=..., max_length=...)`) is authoritative and appears in the OpenAPI schema.
`shared` exports the frontend's copy as a constant (`usernamePattern`) for native form
validation ([react.md](react.md) REACT-11), and a `shared` test asserts that each constant
equals the corresponding `pattern`, `minLength`, or `maxLength` in
`shared/openapi/openapi.json`, so a change on one side fails CI until the other matches.

**MONO-17 — WebSocket messages are part of the contract.** FastAPI does not describe
WebSocket routes in OpenAPI, so the backend adds its WebSocket message models to the
schema's `components.schemas` in a custom `app.openapi()` (FastAPI's documented way to
extend the schema), and MONO-13 generates their types with everything else. Details are in
[websockets.md](websockets.md).
