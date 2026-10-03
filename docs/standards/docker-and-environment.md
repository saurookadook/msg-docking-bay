# Docker and Environment Standards

Applies to `docker-compose.yaml`, workspace Dockerfiles, the reverse proxy, and
environment files.

---

## Environment files

**ENV-1 — Configuration comes from `.env` (development) and `.env.test` (tests) at the
repository root.** Both are git-ignored. Their committed templates, `.env.example` and
`.env.test.example`, MUST list every variable with a safe placeholder. Add a variable to
the templates in the same change that starts reading it.

**ENV-2 — Never commit real secrets.** In templates, a secret gets an obvious placeholder
(`SESSION_SECRET=<generate-your-own-secret>`). Only `.env.test.example` may contain a
throwaway literal secret.

**ENV-3 — Variable names are `SCREAMING_SNAKE_CASE`, grouped and prefixed by the service
they configure:**

```dotenv
APP_DOMAIN=app.example.dev
LOG_LEVEL=DEBUG

FRONTEND_HOST=frontend
FRONTEND_PORT=5173

BACKEND_HOST=backend
BACKEND_PORT=3000
WS_PORT=8080

DB_HOST=mongo
DB_PORT=27017
DB_NAME=app
```

**ENV-4 — Keep the test environment isolated from development.** It uses a different
database name (`test-app`) and different host ports, so tests can run while the dev stack
is up.

---

## Docker Compose

**ENV-5 — Each workspace and each piece of infrastructure is a Compose service**: for
example `frontend`, `backend`, `backend-test`, `mongo`, and `proxy`, plus an aggregate
service so `docker compose up <aggregate>` starts the whole stack. Service names match the
hostnames used in env vars and proxy upstreams.

**ENV-6 — Services load configuration with `env_file`**, not inline `environment` blocks.
A test service `extends` its main service and overrides `env_file` and the build
`target`.

**ENV-7 — Development services bind-mount their workspace source and `shared`.** Each
also mounts an anonymous volume over `node_modules`, so the container keeps its own Linux
install.

**ENV-8 — Persistent local data lives under a git-ignored `.docker/` directory**
(`./.docker/mongodb/data/db/`).

---

## Dockerfiles

**ENV-9 — Each workspace has one multi-stage Dockerfile** with stages named
`<pkg>-base` → `<pkg>-build` → `<pkg>-dev`, plus `<pkg>-test` and `<pkg>-prod`. The build
context is the repository root, so a stage can copy `shared`, `package.json`,
`pnpm-workspace.yaml`, and `pnpm-lock.yaml`. Shared `ARG`/`ENV` values are set once in the
base stage.

**ENV-10 — Base images use the Node major from `.nvmrc`** (`node:24-bookworm`). Enable
pnpm with `corepack enable`, install with a frozen lockfile, and build `shared` before
the workspace itself:

```dockerfile
RUN corepack enable
RUN pnpm install --frozen-lockfile
RUN pnpm shared:base build
RUN pnpm backend:base build
```

**ENV-11 — In dev and test stages, `ENTRYPOINT` runs the root workspace alias and `CMD`
names the script** (`ENTRYPOINT ["pnpm", "backend:base"]`, `CMD ["start:dev"]`). That way
`docker compose run backend <script>` works for any script.

**ENV-12 — Never copy `.env` files into an image.** Provide configuration at runtime
through Compose `env_file` or the deployment platform. Production stages contain only
built output and production dependencies.

---

## Reverse proxy and TLS

**ENV-13 — A reverse proxy (NGINX) is the single public entry point.** It terminates TLS
for `APP_DOMAIN` and routes traffic to upstreams named by role:

- `/api` → `backend` (the NestJS app)
- WebSocket traffic → `websocket`, with `Upgrade` and `Connection` headers
- everything else → `frontend`

**ENV-14 — Generate local TLS certificates with `mkcert`** through a setup script, into a
git-ignored `certs/` directory. Never commit certificates or keys.

**ENV-15 — Frontend and backend code MUST NOT hard-code `localhost` URLs or ports.** Derive
them from configuration (`APP_DOMAIN`, `window.location`) and route traffic through the
proxy.
