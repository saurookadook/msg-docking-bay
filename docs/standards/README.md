# Coding Standards

These standards define how code in this repository is written, organized, tested, and
shipped. The repository has a React and TypeScript frontend, a Python backend (FastAPI,
SQLAlchemy, Alembic, and Pydantic, tested with pytest) on PostgreSQL, real-time messaging
over WebSockets, and a framework-free TypeScript `shared` package that holds the API
contract generated from the backend's OpenAPI schema.

## Documents

### Backend (Python)

The backend's own standards are in [python/](python/README.md):

| Document                                             | Covers                                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| [python/python.md](python/python.md)                 | Version, uv, layout, Ruff, pyright, naming, typing, errors, logging      |
| [python/fastapi.md](python/fastapi.md)               | App, routers, routes, envelopes, dependencies, errors, middleware, crons |
| [python/pydantic.md](python/pydantic.md)             | Entities, request and response models, validators, settings              |
| [python/sqlalchemy.md](python/sqlalchemy.md)         | Base class, models, sessions, facades, queries, upserts, transactions    |
| [python/alembic.md](python/alembic.md)               | Configuration, `env.py`, generating and reviewing migrations, enums      |
| [python/httpx.md](python/httpx.md)                   | Outbound client modules, timeouts, error wrapping, `TestClient`          |
| [python/beautiful-soup.md](python/beautiful-soup.md) | Scraping for data ingestion: fetch/parse split, selectors, fixtures      |
| [python/pytest.md](python/pytest.md)                 | Plugins, layout, fixtures, database tests, factory-boy, mocks            |

### Database

| Document                                           | Covers                                                      |
| -------------------------------------------------- | ----------------------------------------------------------- |
| [relational-databases.md](relational-databases.md) | Modeling, keys, constraints, indexes, queries, migrations   |
| [postgresql.md](postgresql.md)                     | Version, types, IDs, search, roles, connections, containers |

### Frontend and `shared` (TypeScript)

| Document                                               | Covers                                                           |
| ------------------------------------------------------ | ---------------------------------------------------------------- |
| [typescript.md](typescript.md)                         | Types, naming, functions, classes, imports, comments             |
| [nodejs.md](nodejs.md)                                 | Runtime, pnpm, modules, env vars, async, crypto                  |
| [react.md](react.md)                                   | Components, state store, hooks, routing, client-side data access |
| [css.md](css.md)                                       | CSS / SCSS: file layout, nesting, tokens, selectors              |
| [testing.md](testing.md)                               | Vitest, Jest, Testing Library, MSW, fixtures, custom matchers    |
| [logging-and-errors.md](logging-and-errors.md)         | Shared logger, log levels, error messages, error wrapping        |
| [formatting-and-linting.md](formatting-and-linting.md) | oxfmt, oxlint, suppression comments                              |

### Across the repository

| Document                                               | Covers                                                                  |
| ------------------------------------------------------ | ----------------------------------------------------------------------- |
| [monorepo.md](monorepo.md)                             | Workspaces, the `shared` package, root scripts, the OpenAPI contract    |
| [websockets.md](websockets.md)                         | Event names, message models, FastAPI routes, frontend connection manager |
| [docker-and-environment.md](docker-and-environment.md) | `.env` files, Compose, Dockerfiles, image security, CI, proxy           |
| [github-actions.md](github-actions.md)                 | Workflow layout, change detection, permissions, repo settings           |
| [ci-pipeline.md](ci-pipeline.md)                       | `ci.yml`, per-area checks, setup actions, image publishing              |
| [git-workflow.md](git-workflow.md)                     | Branch names, commit messages, PR titles and template                   |

## Conventions used in these documents

**Example domain.** Examples use one illustrative domain so they read consistently:
**users**, **projects**, and **tasks** (`User`, `Project`, `Task`, `ProjectStatus`;
`userID` and `projectID` in TypeScript, `user_id` and `project_id` in Python and on the
wire). They are placeholders; apply the same patterns to the real entities.

**Package scope.** pnpm workspace packages are shown as `@app/frontend` and
`@app/shared`. Replace `app` with the repository's actual scope. The backend is a uv
project, not a pnpm package ([monorepo.md](monorepo.md) MONO-1).

## How to read a rule

Every rule has an ID so reviews can cite it (for example, "violates `FAPI-7`").

- **MUST / MUST NOT** — required. A review should block on a violation.
- **SHOULD / SHOULD NOT** — the default. Deviate only with a stated reason (a code comment
  or PR note).
- **MAY** — permitted; use judgement.

When two documents seem to conflict, the more specific one wins (for example,
`python/fastapi.md` over `python/python.md` for a route, or `react.md` over
`typescript.md` for a component). Tooling configuration (oxfmt, oxlint, `tsconfig`, Ruff,
pyright, `pytest.ini`) is the final authority on anything it enforces automatically.

## Changing a standard

Standards describe how the code _should_ look, so update the document in the same PR that
deliberately changes a convention. If code and standard disagree and nobody chose that,
fix the code.

The Python documents were copied from the shared standards in `agent-configs`
(`docs/standards/python/`) and adapted to this repository (root scripts, Compose service
names). When pulling a newer version from there, keep those adaptations.
