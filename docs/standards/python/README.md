# Python Standards

These standards cover the backend in `backend/`: a FastAPI service on PostgreSQL through
SQLAlchemy and Alembic, with Pydantic models, outbound HTTP clients, HTML scraping with
Beautiful Soup for data ingestion, and a pytest suite that runs against a real test
database.

They were derived from two reference codebases:

| Codebase             | Role                                                                       |
| -------------------- | -------------------------------------------------------------------------- |
| `aoam-property-plan` | the primary reference: Python 3.12, uv, the layout and patterns below      |
| `nlp-stock-sa`       | the earlier project: Python 3.10, Poetry, Scrapy, NLTK, and VADER          |

Where the two disagree, the newer project (`aoam-property-plan`) wins, because it is
where the patterns were refined. Where both share a habit that causes bugs, the standard
corrects it and says so.

The rules were then checked against current official guidance, collected in
[Python best practices](../../research/python/python-best-practices.md),
[FastAPI best practices](../../research/python/fastapi-best-practices.md),
[Pydantic best practices](../../research/python/pydantic-best-practices.md), and
[SQLAlchemy and Alembic best practices](../../research/python/sqlalchemy-alembic-best-practices.md).
Where that guidance differs from the reference code, the standard follows the guidance,
preferring Python's own documentation (docs.python.org and the PEPs) when sources
disagree: Python 3.14 without `from __future__ import annotations`, Ruff and pyright in
strict mode in place of black, flake8, and editor-only type checking, `X | None` in place
of `Optional`, %-style log arguments in place of f-strings, exception names ending in
`Error`, and docstrings on every public module, class, and function.

## Documents

| Document                               | Covers                                                                    |
| -------------------------------------- | ------------------------------------------------------------------------- |
| [python.md](python.md)                 | Version, tooling, layout, naming, typing, errors, logging, security       |
| [fastapi.md](fastapi.md)               | App, routers, routes, envelopes, dependencies, errors, middleware, crons  |
| [pydantic.md](pydantic.md)             | Entities, request and response models, validators, settings               |
| [sqlalchemy.md](sqlalchemy.md)         | Base class, models, sessions, facades, queries, upserts, transactions     |
| [alembic.md](alembic.md)               | Configuration, `env.py`, generating and reviewing migrations, enums       |
| [httpx.md](httpx.md)                   | Outbound client modules, timeouts, error wrapping, `TestClient`           |
| [beautiful-soup.md](beautiful-soup.md) | Fetch/parse split, parsing tiers, selectors, text extraction, fixtures    |
| [pytest.md](pytest.md)                 | Plugins, layout, fixtures, database tests, factory-boy, requests-mock     |

## How they fit with the rest of the standards

These documents cover the Python code itself. The repository-wide documents in the parent
folder cover everything around it, and apply to the backend as well:

- [../relational-databases.md](../relational-databases.md) and
  [../postgresql.md](../postgresql.md): the database. Where a Python document departs
  from one of them, it names the rule it replaces.
- [../docker-and-environment.md](../docker-and-environment.md): `.env` files, the
  `backend`, `backend-test`, and `backend-migrations` Compose services, and the backend
  Dockerfile.
- [../ci-pipeline.md](../ci-pipeline.md) and [../github-actions.md](../github-actions.md):
  the backend's CI checks.
- [../monorepo.md](../monorepo.md): the root `backend:*` scripts, and the OpenAPI
  contract that the TypeScript types in `shared` are generated from.
- [../websockets.md](../websockets.md): FastAPI WebSocket routes and their message
  models.
- [../git-workflow.md](../git-workflow.md): branches, commits, and PRs.

The TypeScript documents (`typescript.md`, `nodejs.md`, `react.md`, `testing.md`,
`logging-and-errors.md`, `formatting-and-linting.md`) do not apply to Python code.

## Conventions used in these documents

**Example domain.** Examples use the same illustrative domain as the rest of the
standards: **users**, **projects**, and **tasks** (`ProjectDB`, `ProjectEntity`,
`ProjectFacade`, `project_id`). Scraping examples use an external **article** page, since
nothing in that domain is scraped. Apply the same patterns to this app's real entities.

**Paths.** Paths are relative to the backend package root (`backend/`), which is also the
import root: modules import `from models.project.facade import ProjectFacade`, never
`from backend.models...`.

## How to read a rule

Every rule has an ID so reviews can cite it (for example, "violates `SQLA-12`").

- **MUST / MUST NOT** — required. A review should block on a violation.
- **SHOULD / SHOULD NOT** — the default. Deviate only with a stated reason (a code comment
  or PR note).
- **MAY** — permitted; use judgement.

When two documents seem to conflict, the more specific one wins (`sqlalchemy.md` over
`python.md` for a model class). Tool configuration (Ruff, pyright, `pytest.ini`) is the
final authority on anything it enforces automatically.
