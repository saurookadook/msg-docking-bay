# Plan: Phase 2 — Ingest service scaffold

## Context

Phase 2 of [`data-ingestion.md`](data-ingestion.md) creates the `ingest/` service that Phases 3–5 fill in.
ADR 0002 makes it a separate uv and moon project that **imports the backend** rather than copying it:

- The backend owns the schema and its migrations, the models, constants, config, the DB session and
  logging.
- The ingest service only writes rows.

Phase 1's PR A (#16) is on `main`, so `sources` and `ingest_runs` exist, and that is all Phase 2 needs.
PR B (mobile suits) and PR C (people) are not built yet, and both must land before Phase 3a.

**Outcome:** one PR that adds the following, and no upstream calls yet:

- `ingest/`, with a single `ingest` package.
- A CLI (`python -m ingest`) with a `status` command.
- Run tracking on `ingest_runs`, and a schema-at-head guard.
- A Docker image, an `ingest` Compose service, and an `ingest:test` task.

## Design decisions (agreed 2026-11-05)

- **Reuse the backend as much as possible.** The backend is an editable path dependency:
  `msg-docking-bay-backend = { path = "../backend", editable = true }`.
  - Ingest imports `config.env_vars` (`EnvVarManager`), `db.db_session_manager` (`DBSessionManager`),
    `models.*`, `constants.catalog` (`SourceKind`, `IngestRunStatus`) and `utils.logging.init`
    (`init_logging`) exactly as the backend does.
  - Imports go one way only: ingest → backend.
- **Ingest's own code lives under one top-level package, `ingest/ingest/`.** The editable install puts
  the backend's top-level packages on `sys.path`, so a flat `config/` or `services/` in ingest would
  shadow them, or be shadowed. Paths in later phases become `ingest/ingest/services/<upstream>.py`,
  `ingest/ingest/parsers/` and `ingest/ingest/loaders/`.
- **Phase 3's Pydantic entities and facades go in `backend/models/`.** The ingest loader is their first
  caller.
- **The HTTP config waits for its first caller**, in Phase 3b or Phase 4; Phase 3a only reads a local
  dump. This applies ENV-1: a variable lands with the code that reads it.
  - This covers `INGEST_USER_AGENT`, the rate limits and the User-Agent builder.
  - When they arrive, they go in `ingest/ingest/config.py` as `IngestEnvVars(EnvVars)`. The subclass
    inherits `DATABASE_*` and the `_FILE` secret handling. The backend's `extra="ignore"` skips
    `INGEST_*`.
  - **Phase 2 adds no env vars**, so `.env.example` stays as it is.
- **There is no Compose dependency on migrations. The CLI checks the schema instead.** Every command
  that writes checks that the database is at the Alembic head first. If it isn't, it fails and says to
  run `moon run backend:migrate`. Ingest never migrates, because it connects as the app role, which
  has DML rights only (`postgres/initdb/01-create-roles.sh`).
- **Concurrency:**
  - One run per source kind at a time, enforced by a session-level advisory lock held for the length
    of the run. The lock is released automatically if the process dies.
  - Once the lock is held, any leftover `running` row for that kind is from a crashed run. It is
    marked `failed` with `error_summary = 'abandoned'`.
  - None of this needs a schema change.
- **The run row is committed separately from the data writes**, so a rolled-back load still leaves its
  `failed` row behind.
- **Reuse the backend's test code** (`_factories`, `_mocks`, the rollback-per-test session and the
  upgrade at session start) rather than copying it. Step 2 checks how this resolves.

## Layout

```txt
ingest/
  pyproject.toml  uv.lock  .python-version  moon.yml  CLAUDE.md  Dockerfile
  pytest.ini  pytest.ci.ini  conftest.py
  ingest/
    __init__.py
    __main__.py        sys.exit(main())
    cli.py             argparse, subcommand registry (PY-35, PY-36)
    schema.py          assert_schema_at_head()
    runs.py            track_run(), RunStats, latest_watermark()
    errors.py          IngestError, SchemaNotAtHeadError, RunInProgressError
    _tests/            test_cli.py, test_schema.py, test_runs.py
scripts/ingest-test.sh
```

## Implementation order and checkpoints

Each **Checkpoint** marks where a commit belongs. Commits are made by hand, not by an agent: at each
checkpoint the agent stops and reports what changed and how it was verified. The messages below are
suggestions. Branch: `feat/add-ingest-service`.

### 0. Docs (Checkpoint → `docs(docs): plan the phase 2 ingest service`)

- Save this plan to `docs/plans/phase-2-ingest-service.md`.
- Update `docs/plans/data-ingestion.md`:
  - Phase 2: link to this plan; record the `ingest/ingest/` package, the deferred HTTP config, and the
    schema guard in place of a Compose dependency on migrations.
  - Architecture decisions: change `ingest/services/<upstream>.py` to `ingest/ingest/services/…`.
  - Phase 3a: change the `ingest/services/` and `ingest/parsers/` paths the same way.
- Leave `docs/standards/` alone, since those standards are generic.

### 1. Commit scope (Checkpoint → `chore(repo): add the ingest scope to commit conventions`)

- Add an `ingest` row to the Scope table in `COMMIT_CONVENTIONS.md`: "the ingest service (`ingest/`)".

### 2. uv project (Checkpoint → `build(ingest): scaffold the ingest uv project`)

- **`pyproject.toml`:**
  - `name = "msg-docking-bay-ingest"`, `requires-python = ">=3.14"`.
  - `dependencies = ["msg-docking-bay-backend"]`, plus `[tool.uv.sources]` for the path dependency.
  - `[project.scripts] ingest = "ingest.cli:main"`.
  - Hatch `packages = ["ingest"]`.
  - A dev group matching the backend's: factory-boy, pyright, pytest, pytest-cov, pytest-mock,
    pytest-sugar, pytest-xdist, ruff.
  - `[tool.ruff*]` and `[tool.pyright]` copied from `backend/pyproject.toml`, and coverage `omit`
    likewise. Add `[tool.ruff.lint.isort] known-first-party = ["ingest"]`.
- `.python-version` copied from the backend, then `uv lock`.
- **`moon.yml`:**
  - `language: python`, `stack: backend`, `dependsOn: ['backend']`, so a backend model change re-runs
    ingest's typecheck.
  - **Check first** with `moon project-graph` / `moon query projects`: `enforceLayerRelationships` may
    reject one `application` depending on another. If it does, pick the layer moon allows
    (likely `automation`) and note why in a comment.
  - The python tasks in `.moon/tasks/python.yml` (format, lint, typecheck) are inherited.
- **`CLAUDE.md`:**
  - Import the python README, `python.md`, `sqlalchemy.md` and `pydantic.md`.
  - "Read first when" entries: httpx and beautiful-soup for `ingest/ingest/services/`; pytest for tests;
    docker-and-environment for the Dockerfile and Compose.
  - State the reuse rule: import from the backend; never redefine a model, enum or config field there.
    Schema changes are backend PRs.
- **`pytest.ini` / `pytest.ci.ini`:** mirror the backend's, with `testpaths = ingest`.
- **Reuse spike (report the result at the checkpoint):**
  - Confirm that `import _factories.source.db` and `import _mocks.temporal` resolve under both pytest
    and pyright strict through Hatchling's editable `.pth`.
  - If pyright doesn't follow it, add `extraPaths = ["../backend"]`.
  - If they aren't importable at all, add `_factories` and `_mocks` to the backend's hatch `packages`
    (a separate `build(backend)` commit). PY-7 still holds, since only `_tests/` code imports them.
- **`conftest.py`:** reuse the backend's fixtures. Either load them with `pytest_plugins` from a small
  module moved out of `backend/conftest.py`, or import them directly.
  - Ingest must not pull in `api.app.main`; the backend conftest imports it for `test_app_client`.
  - The likely result is a `backend/db/testing.py`, holding `alembic_config()`, the session-start
    upgrade and `test_db_session`, that both conftests use. That is a `refactor(backend)` commit before
    this one, if needed.
  - Force `ENVIRONMENT=test` and `DATABASE_NAME=test_msg_docking_bay` before imports (PYTEST-10).

### 3. Schema guard (Checkpoint → `feat(ingest): refuse to run against an unmigrated database`)

`ingest/ingest/schema.py`:

- `expected_heads()`: `ScriptDirectory` built from the backend's migrations folder, located through
  `Path(db.migrations.__file__).parent` rather than `alembic.ini`.
- `current_heads(connection)`: `MigrationContext.configure(connection).get_current_heads()`.
- `assert_schema_at_head(connection)` raises `SchemaNotAtHeadError`, naming both revisions and the fix.
- **Tests:**
  - The migrated test database passes.
  - The pure comparison helper rejects a behind or unknown revision, and an empty database. This
    avoids downgrading the shared test database.

### 4. Run tracking (Checkpoint → `feat(ingest): record each run in ingest_runs`)

`ingest/ingest/runs.py`:

- `RunStats` (dataclass) holds `pages_seen`, `rows_written`, `error_count` and `watermark_at`. The job
  mutates it.
- **`track_run(kind, *, session_factory)`** (contextmanager) yields `RunStats`:
  1. Hold the lock on a dedicated `DBSessionManager().engine` connection:
     `pg_try_advisory_lock(<namespace const>, hashtext(:kind))`. If the lock is taken, raise
     `RunInProgressError`.
  2. In one short transaction, mark leftover `running` rows of `kind` as `failed` / `abandoned` with
     `finished_at = now()`, then insert the new `running` row and commit.
  3. **On normal exit:** set `succeeded`, `finished_at`, the counts and `watermark_at`, and commit.
  4. **On an exception:**
     - Set `failed`, the counts so far, and `error_summary = summarize_error(exc)`, then commit and
       re-raise.
     - `summarize_error` returns `"<sqlstate> <constraint>"` for a `DBAPIError` (through `orig.sqlstate`
       and `diag.constraint_name`), and the exception class name otherwise. It never includes message
       text or row data; this follows the `error_summary` docstring in `models/ingest_run/db.py`.
  5. Unlock in a `finally`.
- **`latest_watermark(session, kind)`:** the `watermark_at` of the newest `succeeded` run, ordered by
  `started_at`, which `ix_ingest_runs_source_kind_status_started_at` serves. Phase 3b is its caller,
  but it is small and fixed by the Phase 1 design.
- **`session_factory`** defaults to the `DBSessionManager().scoped_session.session_factory`. Tests pass
  a `sessionmaker` bound to the test connection with `join_transaction_mode="create_savepoint"`, so
  "commits" become savepoints and the outer rollback cleans up.
- **Tests** (classes, sentence names, PYTEST-7):
  - Success records `succeeded`, the counts and the watermark.
  - A raised error records `failed` with only an SQLSTATE and constraint name, and re-raises.
  - A loader `IntegrityError` that rolls back still leaves the `failed` row.
  - A second concurrent run of the same kind raises `RunInProgressError`; a different kind is allowed.
  - A leftover `running` row is marked `abandoned`.
  - `latest_watermark` ignores failed and running runs and returns `None` when there are none.
  - Time comes from `mock_utcnow` / the DB, with no sleeps.

### 5. CLI (Checkpoint → `feat(ingest): add the ingest CLI with a status command`)

- **`cli.py`:** `main(argv: Sequence[str] | None = None) -> int` (PY-36).
  - It calls `init_logging(app_name="ingest")` once (PY-38).
  - It uses argparse subparsers, built from a registry `COMMANDS: dict[str, Command]` (PY-35). Later
    phases add `fandom`, `wikidata` and others as one module and one entry each.
- **`ingest status`:** checks the schema, then prints, for each `SourceKind`, the latest run's status,
  start and finish times, counts, and the current watermark.
- **`run_source_job(kind, job)`:** the helper every source command uses later: the schema guard, then
  `track_run`, then `job(session, stats)`.
- **Exit codes:**
  - `0` success.
  - `1` an `IngestError`, such as a schema mismatch or a run in progress, logged with its message.
  - `2` an argparse usage error.
  - Unexpected exceptions propagate with a traceback.
- **Tests:**
  - `main(["status"])` returns 0, and its output (from `capsys`) lists every source kind.
  - `main([])` exits 2 and prints usage.
  - `run_source_job` maps a `SchemaNotAtHeadError` to 1 (by monkeypatching the guard).

### 6. Docker and moon (Checkpoint → `build(docker): add the ingest service to Compose`)

- **`ingest/Dockerfile`** (ENV-14 shape):
  - Stages: `ingest-base` → `ingest-dev` → `ingest-test`, and `ingest-build` → `ingest-prod`.
  - It uses the same pinned `PYTHON_IMAGE` and `UV_IMAGE` digests as `backend/Dockerfile`.
  - The backend arrives as the named build context `backend`. `COPY --from=backend . /app/backend`
    happens before `uv sync --locked --no-install-project`, in `WORKDIR /app/ingest`, so `../backend`
    resolves.
  - `ingest-test` runs `CMD ["pytest", "-c", "pytest.ci.ini"]`.
  - `ingest-prod` uses tini and a non-root `app` user, and smoke-tests `python -c "import ingest.cli"`.
  - The `docker-bake.hcl` target and the publish task wait for Phase 5, where deployment is decided.
- **`compose.yaml`:**
  - **`ingest`:**
    - `build: { context: ./ingest, target: ingest-dev, additional_contexts: { backend: ./backend } }`.
    - `profiles: [ingest]`, `env_file: [.env]`, `entrypoint: ["python", "-m", "ingest"]`.
    - The app role: `DATABASE_PASSWORD_FILE: /run/secrets/db_app_password`, with
      `secrets: [db_app_password]`.
    - It mounts `./ingest:/app/ingest` and `./backend:/app/backend` (like `backend-migrations`), so it
      runs current code without a rebuild.
    - `depends_on: postgres` (healthy), `logging: *logging` and `no-new-privileges`.
    - Usage: `docker compose --profile ingest run --rm ingest status`.
  - **`ingest-test`:** extends `ingest` (ENV-8) with `profiles: [test]`, `target: ingest-test` and
    `env_file: [.env.test]`.
    - It uses the owner role, because the suite migrates.
    - It redeclares `depends_on` and drops the source mounts so it tests the image.
- **`scripts/ingest-test.sh`:** a copy of `scripts/backend-test.sh` that runs `ingest-test` in the same
  `msg-docking-bay-test` project.
- **`ingest/moon.yml`:** a `test` task (the script, `cache: false`, `mutex: 'compose-test-db'`,
  `runFromWorkspaceRoot`, `runInCI: false`), mirroring `backend/moon.yml`.
- **`.github/dependabot.yml`:** add `uv` for `/ingest`, and add `/ingest` to the docker directories.

### PR — `feat(ingest): add the ingest service scaffold`

Fill in `.github/pull_request_template.md`.

## Risks to check during implementation

- **moon layer rules versus `dependsOn: ['backend']`** (step 2). The result decides ingest's `layer`.
- **pyright strict and the editable path dependency:** check whether it resolves the backend's
  packages, and whether `extraPaths` is needed.
- **Ruff import sorting:** it treats backend packages as third-party, which is acceptable. Don't fight
  it with `known-first-party` for the backend's names.
- **`DBSessionManager` defaults:**
  - It sets `application_name` to `app-backend`, so ingest connections are labeled as backend ones in
    `pg_stat_activity`.
  - It has `statement_timeout=10s`, which is fine for Phase 2, but Phase 3a's bulk upserts may need
    batching or a per-session `SET`.
  - Note both rather than changing the backend now. If ingest needs its own label, the fix is a small
    `DATABASE_APPLICATION_NAME` field in a `feat(backend)` commit.
- **uv lock and Docker cache:** copying all of `backend/` before `uv sync` means any backend change
  rebuilds ingest's dependency layer. That is acceptable at this size.

## Verification

- Prefix moon commands with `export PATH="$HOME/.proto/shims:$HOME/.proto/bin:$PATH"`.
- `moon run ingest:lint ingest:format ingest:typecheck` (Ruff and pyright strict).
- `moon run ingest:test`: pytest in Compose against a fresh PostgreSQL 18, with the migrations applied
  at session start. `moon run backend:test` must still pass, especially if `backend/conftest.py` was
  refactored.
- **End to end on the dev database:**
  - `moon run backend:migrate`, then `docker compose --profile ingest run --rm ingest status` exits 0
    and lists every source kind with no runs.
  - Run `alembic downgrade -1` through `backend-migrations`; `ingest status` now exits 1 with the
    migrate hint. Then upgrade again.
  - `docker compose --profile ingest run --rm ingest --help` shows the registry.
- `docker build` of the `ingest-prod` target succeeds, including its smoke import.
