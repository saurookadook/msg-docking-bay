# ingest

The batch ingest service: a CLI (`python -m ingest`) that loads upstream catalog data
into PostgreSQL. It is a uv project (`pyproject.toml`, `uv.lock`) that installs the
backend as an editable path dependency, and it follows the backend's coding standards,
imported below. The decision is in `docs/decisions/0002-data-ingestion.md` and the plans
are in `docs/plans/` (`data-ingestion.md`, `phase-2-ingest-service.md`).

@../docs/standards/python/README.md
@../docs/standards/python/python.md
@../docs/standards/python/pydantic.md
@../docs/standards/python/sqlalchemy.md

## Reuse the backend, never copy it

- Import the backend's packages exactly as the backend does: `config.env_vars`,
  `db.db_session_manager`, `models.<entity>.db`, `constants.catalog`,
  `utils.logging.init`. Never redefine a model, enum, constant or `EnvVars` field here.
- **The backend owns the schema.** A new table, column or enum type is a backend PR with
  its migration, landed before the ingest code that writes it. Ingest only writes rows,
  as the app role, and never migrates.
- Pydantic entities and facades live in `backend/models/<entity>/`, even when ingest is
  their first caller.
- Ingest-only settings go in `ingest/config.py` as a subclass of the backend's `EnvVars`.
- **All ingest code lives under the `ingest` package** (`ingest/ingest/`). The backend's
  top-level packages share this environment, so a top-level `config/` or `services/`
  here would shadow them.
- Tests reuse the backend's test support: `_fixtures.db` (loaded in `conftest.py`),
  `_factories` and `_mocks`.
- **Shared dependencies lock to the backend's versions.** After `uv lock` here, or after
  an upgrade in `backend/uv.lock`, run `moon run ingest:lock-drift`. It lists every
  package the two lockfiles hold at different versions and prints the `uv lock -P …`
  command that realigns this one. The pre-commit hook runs it when either lockfile is
  staged, and CI's `repo` job runs it on every PR and push.

## Read first when the task touches

- **Outbound HTTP or a dump file**: a module in `ingest/services/`. Read
  `docs/standards/python/httpx.md` and `docs/standards/python/beautiful-soup.md`, and the
  source rules in ADR 0002: no requests to `gundam.fandom.com` without written
  permission on file, an identified User-Agent, and no attempt to get past a bot
  challenge.
- **Database design or queries**: read `docs/standards/relational-databases.md` and
  `docs/standards/postgresql.md`.
- **Tests**: anything under `_tests/` or `conftest.py`. Read
  `docs/standards/python/pytest.md`.
- **Container or env vars**: the Dockerfile, a Compose service, or `.env*` files. Read
  `docs/standards/docker-and-environment.md`.
