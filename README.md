# msg-docking-bay

A React + Vite frontend and a FastAPI backend on PostgreSQL 18. Locally the stack runs
in Docker Compose behind an NGINX proxy at **<https://msg-docking-bay.dev>**, and
[moon](https://moonrepo.dev) runs every task.

| Path                   | What                                                              |
| ---------------------- | ----------------------------------------------------------------- |
| `frontend/`            | React UI (pnpm project)                                           |
| `backend/`             | FastAPI service, SQLAlchemy, Alembic (uv project)                 |
| `nginx-reverse-proxy/` | NGINX proxy config, and the local TLS certificates in `certs/`    |
| `postgres/`            | PostgreSQL init scripts                                           |
| `scripts/`             | local setup and test helpers                                      |
| `docs/`                | [coding standards](docs/standards/README.md), decisions, research |

## Setup

Prerequisites: [Docker Desktop](https://docs.docker.com/desktop/) and
[mkcert](https://github.com/FiloSottile/mkcert).

```sh
# 1. Install proto, then the pinned tools in .prototools (moon, Node, pnpm, Python, uv)
bash <(curl -fsSL https://moonrepo.dev/install/proto.sh)
proto install

# 2. Generate moon's config schemas and install the pre-commit hook
moon sync config-schemas
moon sync vcs-hooks

# 3. Create .env, .env.test, TLS certificates, and database passwords (never overwrites)
moon run root:setup

# 4. Point the domain at your machine
sudo sh -c 'echo "127.0.0.1 msg-docking-bay.dev" >> /etc/hosts'

# 5. Start the stack, then apply migrations (in a second terminal)
moon run root:dev
moon run backend:migrate
```

The proxy publishes ports 80 and 443 on 127.0.0.1 (`PROXY_BIND_ADDRESS`). Docker Desktop
needs **Settings → Advanced → Allow privileged port mapping** for those. Otherwise, in
`.env`, either set `PROXY_HTTP_PORT` and `PROXY_HTTPS_PORT` to free ports (e.g. 8080 and
8443) and browse to `https://msg-docking-bay.dev:8443`, or set `PROXY_BIND_ADDRESS=0.0.0.0`,
which also opens the stack to your network.

## Common commands

| Command                                 | Does                                                           |
| --------------------------------------- | -------------------------------------------------------------- |
| `moon run root:dev`                     | start the stack (`all` service); source changes sync live      |
| `moon run root:down`                    | stop and remove the stack; database data is kept               |
| `moon run :format :lint :typecheck`     | all static checks                                              |
| `moon run :format-write :lint-fix`      | fix formatting and autofixable lint                            |
| `moon run frontend:test`                | frontend tests (Vitest)                                        |
| `moon run backend:test`                 | backend tests (pytest) against a throwaway database            |
| `moon run backend:migrate`              | apply migrations                                               |
| `docker compose run --rm backend-migrations revision --autogenerate -m "..."` | create a migration |
| `docker compose down -v`                | reset everything, including the database volume                |

More detail, including how configuration, secrets, and database roles fit together, is
in [docs/local-development.md](docs/local-development.md).
