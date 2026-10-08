# backend

The FastAPI service: the HTTP API and the WebSocket routes, on PostgreSQL through
SQLAlchemy and Alembic. It is a uv project (`pyproject.toml`, `uv.lock`), not a pnpm
workspace. Code here follows the coding standards imported below. The standards use a
placeholder users/projects/tasks domain; apply their patterns to this app's real
entities.

@../docs/standards/python/README.md
@../docs/standards/python/python.md
@../docs/standards/python/fastapi.md
@../docs/standards/python/pydantic.md
@../docs/standards/python/sqlalchemy.md

## Read first when the task touches

- **Migrations**: anything under `db/migrations/`, `alembic.ini`, or an enum type. Read
  `docs/standards/python/alembic.md`.
- **Database design or queries**: a new table, column, index, constraint, or search
  query. Read `docs/standards/relational-databases.md` and
  `docs/standards/postgresql.md`.
- **Tests**: anything under `_tests/`, `_factories/`, `_mocks/`, `_fixtures/`, or a
  `conftest.py`. Read `docs/standards/python/pytest.md`.
- **Outbound HTTP or scraping**: a module in `services/` that calls an external API or
  parses HTML (data ingestion). Read `docs/standards/python/httpx.md` and
  `docs/standards/python/beautiful-soup.md`.
- **Real-time messaging**: anything under `api/websockets/` or a WebSocket message model.
  Read `docs/standards/websockets.md`.
- **The API contract**: a route, a request or response model, or an entity a response
  contains. Read `docs/standards/monorepo.md` (MONO-13 to MONO-17), then run
  `pnpm api:generate` and commit the result.
- **Container or env vars**: the Dockerfile, a Compose service, `.env*` files, or
  `config/env_vars.py`. Read `docs/standards/docker-and-environment.md`.
- **CI**: `.github/workflows/backend-*.yml` or `.github/actions/python-setup/`. Read
  `docs/standards/ci-pipeline.md`.
