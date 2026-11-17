# Plan: PR A — generated API contract

> **Agreed** 2026-11-17 (grilled the same day). Expands the PR A section of
> [`catalog-read-api.md`](catalog-read-api.md). No code until asked.

Branch `build/generate-api-contract`. PR title:
`build(frontend): generate API types from the backend's OpenAPI schema`.

## Context

PR B's last step runs `api:generate`, which doesn't exist yet. PR A adds it: the backend's OpenAPI
schema becomes the frontend's source of truth for API types (MONO-13 to MONO-15). The PR proves this
on the one route that exists, the health check, and adds the typed Mirage endpoint table from
[`catalog-read-api.md`](catalog-read-api.md) D1 and D7. Mock mode for the running app, also from D7,
is a follow-up PR (see the end).

**Facts checked in the repo that shape this plan:**
- `backend/api/app/main.py` imports safely: every `EnvVars` field has a default, the engine is built
  lazily in `DBSessionManager`, and `init_logging` installs a handler without printing. The script
  still writes to a file, not stdout, so a stray log line can't corrupt the JSON.
- `HealthCheckStatus.status` is already `Literal["ok"]`, so the generated type is `'ok'`.
- There is no `backend/scripts/` package, and `testpaths` in `pytest.ini` and `pytest.ci.ini` doesn't
  list one. The backend Dockerfile's `COPY . .` puts `scripts/` in the test image, and in the prod
  image too. That's accepted: it's small and runs only when invoked.
- CI today is `ci.yml` → `repo-lint.yml` (the lockfile job only). There's **no `node-setup` action and
  no `backend-test.yml`**, which is where CI-9 puts the `contract` job.
- `frontend/` is the Node root (D1 Option 1). There's no root `package.json` or `.nvmrc`, only
  `frontend/.nvmrc`. Generated files go in `frontend/src/api/generated/`.
- `uv`, `pnpm` and `node` are on the host PATH through proto shims.

## Steps (one checkpoint each; commits are made by hand)

### 1. Export script → `feat(backend): add an OpenAPI schema export script`
- `backend/scripts/__init__.py` (empty) and `backend/scripts/export_openapi.py`, a PY-36 runnable
  module: `main(argv) -> int`, argparse with one positional `output` path. It writes
  `json.dumps(app.openapi(), sort_keys=True, indent=2)` plus a trailing newline, creating parent dirs.
- Add `scripts` to `testpaths` in both `backend/pytest.ini` and `backend/pytest.ci.ini`.
- Test `backend/scripts/_tests/test_export_openapi.py`: run `main([tmp_path / "openapi.json"])`,
  then assert exit 0, valid JSON, sorted top-level keys, and that `/api/health-check` has operation ID
  `read_health_check`. No database fixture is needed.
- Ruff and pyright strict cover the new package.

### 2. Generator → `build(frontend): generate API types with openapi-typescript`
- `pnpm add -D openapi-typescript@7.13.0` (the version validated in `catalog-read-api.md` Risks).
- `frontend/package.json` script `api:generate`. It runs on the host, as CI does:
  `uv --directory ../backend run python -m scripts.export_openapi ../frontend/src/api/generated/openapi.json && openapi-typescript src/api/generated/openapi.json -o src/api/generated/api.ts && oxfmt src/api/generated`
  (`uv --directory` changes the working directory, so the output path is relative to `backend/`.)
- A `frontend/moon.yml` task `api-generate` (`pnpm run api:generate`, `utility` preset). There's no
  cache, because its inputs live in `backend/`.
- `.oxlintrc.json` `ignorePatterns` gains `src/api/generated/**` (FMT-11). oxfmt still formats it.
- Commit the generated `openapi.json` and `api.ts`.

### 3. First consumer → `refactor(frontend): use the generated health check types`
- New `frontend/src/api/index.ts`: MONO-15 aliases under the backend models' names,
  `HealthCheckStatus` and `HealthCheckResponse`, from `components['schemas']`.
- Delete `HealthCheck` and `HealthCheckResponse` and the TODO from `src/types/index.ts`, leaving
  `Nullable`.
- Rename `HealthCheck` to `HealthCheckStatus`, importing from `@/api`, in `store/health/actions.ts`
  and `store/health/reducer.types.ts`. The `healthCheck` state field keeps its name. Repoint
  `__mocks__/healthMocks.ts`, `utils/safeFetch.test.ts` and the `safeFetch.ts` doc example to `@/api`.

### 4. Endpoint table → `refactor(frontend): drive the Mirage server from an endpoint table`
- `src/__mocks__/endpoints.ts`:
  - `type ApiGetPath`: keys of `paths` that have a `get` operation.
  - `type OkBody<P>`: `paths[P]['get']['responses'][200]['content']['application/json']`.
  - `EndpointConfig<P>`, `{ path: P; handler: (request) => OkBody<P> }`, plus the mapped union
    `AnyEndpointConfig`, so each entry is checked against its own path.
  - `buildRoutePath(path)`: strip the leading `/api`, then `{x}` → `:x`.
  - `paginate(items, request)`: reads `limit` and `offset` and returns `{ data, meta: { limit, offset, total } }`
    (D3). It's typed generically for now; PR B's list routes pin its shape.
  - `endpointConfigs`: one entry for `/api/health-check`.
- `mirageServer.ts`: replace the hand-written `this.get('/health-check', …)` with a loop over
  `endpointConfigs`. The signature and `overrides` ordering don't change.
- `endpoints.test.ts`:
  - The route builder cases `/api/health-check` → `/health-check` and
    `/api/mobile-suits/{mobile_suit_slug}` → `/mobile-suits/:mobile_suit_slug`.
  - `paginate` cases: the first page, and an offset past the end giving an empty `data`.
  - An `it('rejects …')` block that builds configs without registering them, with `@ts-expect-error`
    and a reason (TEST-22) for an unknown path and a wrong body shape. `tsc -b` checks it through
    `tsconfig.test.json`. There's no separate typecheck test file.
- Existing health check tests and stories pass unchanged.

### 5. Standards → `docs(standards): describe the typed Mirage endpoint table`
- `testing.md` TEST-18: a generic paragraph on the endpoint table and typed path keys, using the
  standards' placeholder domain.
- `monorepo.md` MONO-13 to MONO-15: note that this repo generates into `frontend/src/api/` because
  `frontend/` is the Node root (D1).
- `ci-pipeline.md` CI-5: note that `node-setup` reads `frontend/package.json`, `frontend/.nvmrc` and
  `frontend/pnpm-lock.yaml` here, for the same reason.

### 6. Drift check → `ci(repo): fail when the generated API contract is stale`
- New `.github/actions/node-setup/action.yml` per CI-5, rooted at `frontend/`:
  - `pnpm/action-setup` with `package_json_file: frontend/package.json` and no `version`.
  - `actions/setup-node` with `node-version-file: frontend/.nvmrc`, `cache: pnpm` and
    `cache-dependency-path: frontend/pnpm-lock.yaml`.
  - `pnpm install --frozen-lockfile` with `working-directory: frontend`.
  - Pin each action by SHA, like `python-setup`.
- New `.github/workflows/backend-test.yml` (`on: workflow_call`) with one job for now, `contract`:
  - Checkout (`persist-credentials: false`), `python-setup` (backend), `node-setup`.
  - 🏗️ `pnpm run api:generate` in `frontend/`.
  - 🔎 Print `git diff -- frontend/src/api/generated`, then fail if
    `git status --porcelain -- frontend/src/api/generated` prints anything. This catches edits,
    deletions and new files.
  - A comment notes that CI-9's `check` and `test` jobs join it later, and that path gating arrives
    with the first `changes` job (GHA-6).
- `ci.yml`: a `backend` job that calls it with `permissions: { contents: read }`, and `ci-success`
  changes to `needs: [repo, backend]`.

## Verification
- **Backend:** `moon run backend:test`, plus `uv run ruff format --check . && uv run ruff check . && uv run pyright`.
- **Frontend:** `moon run frontend:typecheck frontend:lint frontend:format frontend:test`, and
  Storybook's HealthCheck stories still render.
- **Contract (from the read-API plan):** delete `src/api/generated/`, run `api:generate`, and confirm
  `git status` shows no change.
- **Drift check works:** temporarily change the health check docstring, regenerate, and run the CI
  step's `git status --porcelain` check locally to see it fail. Then revert.
- **CI:** the PR's `Backend Test / contract` job passes, and `ci-success` waits for it.

## Follow-up PR: mock API mode

Branch `feat/add-mock-api-mode`, after PR A merges, since it uses PR A's endpoint table. PR title:
`feat(frontend): add a mock API mode to the dev server`. Behaviour is as agreed in
[`catalog-read-api.md`](catalog-read-api.md) D7.

### 1. Mock mode → `feat(frontend): add a mock API mode to the dev server`
- `vite.config.ts` `define`:
  `'import.meta.env.MOCK_API': JSON.stringify(command !== 'build' && process.env.MOCK_API === 'true')`.
  `vite-env.d.ts` gains `readonly MOCK_API: boolean`.
- `main.tsx`: before `createRoot`, `if (import.meta.env.MOCK_API)`, await
  `import('@/__mocks__/mirageServer')`, then `makeMirageServer({ environment: 'development' })`.
  Wrap it in an async start function, not a top-level await. The constant `false` lets Vite drop the
  import in builds.
- `compose.yaml` `frontend`: `environment: { MOCK_API: "${MOCK_API:-false}" }`. `.env.example`:
  `MOCK_API=false` under `# Frontend`.
- Root `moon.yml`: a `dev-mock` task, the same as `dev` plus `env: { MOCK_API: 'true' }`, with the
  `server` preset.

### 2. Standards → `docs(standards): document the mock API mode`
- Add `dev-mock` and `MOCK_API` to the task or env tables in `docker-and-environment.md` or
  `nodejs.md`, if those tables list `dev` and `LOG_LEVEL`.

### Verification
- Under `moon run root:dev-mock`, the health check page shows the fixture's values, and the backend's
  log has no `/api/health-check` line.
- Under `moon run root:dev`, the same page load shows the request in the backend's log.
- `pnpm build`, then `grep -r miragejs dist/` finds nothing.
