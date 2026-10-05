# Docker and Environment Standards

Applies to environment files, `compose.yaml` and its override files, the frontend and
backend Dockerfiles, `.dockerignore` files, image builds in CI, production containers,
and the reverse proxy. Node and pnpm rules live in [nodejs.md](nodejs.md); Python and uv
rules live in [python/python.md](python/python.md); the `postgres` service is specified
in [postgresql.md](postgresql.md) (PG-16 to PG-19).

**Source of truth:** `compose.yaml`, `compose.production.yaml`, `frontend/Dockerfile`,
`backend/Dockerfile`, the `.dockerignore` files, `docker-bake.hcl`, `.github/workflows/`,
`.github/dependabot.yml`.

---

## Environment files

**ENV-1 — Configuration comes from `.env` (development) and `.env.test` (tests) at the
repository root.** Both are git-ignored. Their committed templates, `.env.example` and
`.env.test.example`, MUST list every variable with a safe placeholder. Add a variable to
the templates in the same change that starts reading it, and, for the backend, in the
same change that adds its field to `EnvVars` ([python/pydantic.md](python/pydantic.md)
PYD-15).

**ENV-2 — Never commit real secrets.** In templates, a secret gets an obvious placeholder
(`SESSION_SECRET=<generate-your-own-secret>`). Only `.env.test.example` may contain a
throwaway literal secret. Production secrets follow ENV-31.

**ENV-3 — Variable names are `SCREAMING_SNAKE_CASE`, grouped and prefixed by the service
or tool they configure.** The backend's names are the `validation_alias` values in
`EnvVars`; Uvicorn reads its own `UVICORN_*` variables
([python/fastapi.md](python/fastapi.md) FAPI-2).

```dotenv
APP_DOMAIN=app.example.dev
ENVIRONMENT=dev
LOG_LEVEL=DEBUG

FRONTEND_HOST=frontend
FRONTEND_PORT=5173

BACKEND_HOST=backend
UVICORN_PORT=8000
UVICORN_WORKERS=1
UVICORN_FORWARDED_ALLOW_IPS=<proxy address>
UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN=20

DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=app
DATABASE_USER=app
DATABASE_PASSWORD=<generate-your-own-secret>
LOG_SQL=false
```

`ENVIRONMENT` is one of `dev`, `test`, or `prod`, matching `NODE_ENV` on the frontend
([nodejs.md](nodejs.md) NODE-11). The backend reads it only through `EnvVars` and
predicate helpers (`is_prod()`), never by comparing strings inline.

**ENV-4 — Keep the test environment isolated from development.** It uses a different
database name (`test_app`, the name the test suite also forces, pytest.md PYTEST-10) and
runs as its own Compose project, with its own containers, network, and volumes, so tests
can run while the dev stack is up. The root `backend:test` script wraps this
([monorepo.md](monorepo.md) MONO-11):
`docker compose -p app-test --env-file .env.test run --rm backend-test`, then
`docker compose -p app-test down -v`.

---

## Docker Compose

**ENV-5 — The Compose file is `compose.yaml` at the repository root, with a top-level
`name:` and no `version:` key** (`version` is obsolete and only triggers a warning). Use
the `docker compose` plugin, Compose 2.33.1 or later (the v5 line recommended), with
Buildx installed; never the legacy `docker-compose` v1 binary.

**ENV-6 — Each runnable workspace and each piece of infrastructure is a Compose
service**, named to match the hostname used in env vars and proxy upstreams: `frontend`,
`backend`, `postgres`, `proxy`. Core services have no `profiles`, so
`docker compose up` starts the stack. Put optional services under a profile instead of
adding an aggregate service:

| Service              | Profile | Runs                                                                 |
| -------------------- | ------- | -------------------------------------------------------------------- |
| `backend-test`       | `test`  | the pytest suite against the test database (ENV-29)                  |
| `backend-migrations` | `tools` | `alembic`, as the database owner role ([postgresql.md](postgresql.md) PG-13) |

`backend-migrations` extends `backend`, sets `entrypoint: ["alembic"]`, and connects with
the owner role's credentials, so `docker compose run --rm backend-migrations upgrade head`
and `... revision --autogenerate -m "..."` work as written in
[python/alembic.md](python/alembic.md). Running a profiled service by name enables its
profile automatically.

**ENV-7 — Services load configuration with `env_file`.** Compose also reads `.env` to
interpolate `${VAR}` in `compose.yaml`, but that alone passes nothing to a container. Use
`environment` only for interpolated values (`POSTGRES_DB: ${DATABASE_NAME}`), fixed
constants (`ENVIRONMENT: dev`), and `<NAME>_FILE` pointers to secrets. Never put a secret
literal in `environment`, and never set one key in both places: `environment` wins.

**ENV-8 — A test service `extends` its main service** and sets its own `profiles`,
build `target`, and `env_file: [.env.test]`. `extends` merges `env_file` lists rather than
replacing them, so `backend-test` loads `.env` and then `.env.test`: `.env.test` MUST
redefine every key whose test value differs, and CI creates `.env` from `.env.example`.
`extends` does not copy `depends_on`, so the test service redeclares it.

**ENV-9 — Development services SHOULD receive source changes through Compose Watch**
(`docker compose up --watch`). Dev images contain their own dependencies (ENV-17), and
host dependency folders are never synced or bind-mounted into a container: `node_modules`
and `.venv` hold binaries built for the host's platform.

```yaml
frontend:
  develop:
    watch:
      - { action: sync, path: ./frontend/src, target: /repo/frontend/src }
      - { action: sync+exec, path: ./shared/src, target: /repo/shared/src,
          exec: { command: [pnpm, shared:base, build] } }
      - { action: rebuild, path: ./pnpm-lock.yaml }
backend:
  develop:
    watch:
      - { action: sync, path: ./backend, target: /app, ignore: [.venv/] }
      - { action: rebuild, path: ./backend/pyproject.toml }
      - { action: rebuild, path: ./backend/uv.lock }
```

The backend's dev server (`fastapi dev`, ENV-19) reloads when synced files change. A
source bind mount MAY replace Watch; the backend image keeps its environment in
`/opt/venv` (ENV-17), outside `/app`, so a mount over `/app` cannot hide it. Run
`docker compose up --build` after dependency changes. Turn on watcher polling only if
file watching is shown to be broken.

**ENV-10 — Database data lives in a named volume, never a bind mount**
([postgresql.md](postgresql.md) PG-16). Other git-ignored local files (generated secrets,
init scripts' inputs, seed data) live under `.docker/`.

**ENV-11 — Every long-running service defines a `healthcheck`, and dependents wait with
`condition: service_healthy`;** otherwise Compose waits only until a container is running.
The backend waits for `postgres` (with `restart: true`, PG-16) and the proxy for its
upstreams. Use exec-form checks with a binary the image has: slim images have `python`
or `node`, not `curl`. The backend's check calls `GET /api/health-check`
([python/fastapi.md](python/fastapi.md) FAPI-3), which touches no database:

```yaml
backend:
  healthcheck:
    test:
      - CMD
      - python
      - -c
      - 'import os, urllib.request; urllib.request.urlopen(f"http://127.0.0.1:{os.environ[''UVICORN_PORT'']}/api/health-check", timeout=2)'
    interval: 10s
    timeout: 5s
    retries: 5
```

`urlopen` raises on a non-2xx response, so the check fails without parsing anything.

**ENV-12 — Only the proxy publishes host ports, and in development it binds them to
loopback** (`"127.0.0.1:443:8443"`). Docker publishes on every interface by default. Other
services are reached by service name. If you need a local database GUI, publish
`127.0.0.1:5432:5432` only while you use it (PG-18).

**ENV-13 — PostgreSQL runs with separate roles and file-based passwords: MUST in
production, SHOULD in development.** The `postgres` image takes its superuser password
from `POSTGRES_PASSWORD_FILE`, and the owner and application roles of PG-13 get theirs
from Compose secrets, generated by the setup script under `.docker/secrets/` and read by
an init script (PG-19). The backend connects as the application role, migrations as the
owner role (ENV-6), and the superuser is for administration only.

---

## Dockerfiles

**ENV-14 — Each runnable workspace has one multi-stage Dockerfile:**

| Image      | Dockerfile            | Build context        | Stages                                                                       |
| ---------- | --------------------- | -------------------- | ---------------------------------------------------------------------------- |
| `frontend` | `frontend/Dockerfile` | the repository root  | `frontend-base` → `frontend-build` → `frontend-dev`, `frontend-test`, `frontend-prod` |
| `backend`  | `backend/Dockerfile`  | `backend/`           | `backend-base` → `backend-dev` → `backend-test`; `backend-build` → `backend-prod` |

The frontend's context is the root so a stage can copy `shared`, `package.json`,
`pnpm-workspace.yaml`, and `pnpm-lock.yaml`. The backend is a self-contained uv project
that imports nothing from the other workspaces, so its context is its own directory.
Shared `ARG`/`ENV` values are set once in the base stage.

**ENV-15 — Every Dockerfile starts with `# syntax=docker/dockerfile:1` and
`# check=error=true`.** The first pins builders to the current Dockerfile frontend; the
second makes build-check violations (secrets in `ARG`/`ENV`, shell-form `CMD`, copying an
ignored file) fail the build. Skip a check only with `# check=skip=<Name>` and a comment.

**ENV-16 — Each build context has a `.dockerignore`.** The root one MUST exclude
`**/node_modules`, `**/dist`, `**/coverage`, `**/*.log`, `**/.env`, `**/.env.*`,
`**/.npmrc`, `.git`, `.docker/`, `certs/`, and `backend/`. `backend/.dockerignore` MUST
exclude `.venv`, `**/__pycache__`, `.pytest_cache`, `.ruff_cache`, `.coverage`,
`htmlcov`, `**/.env`, and `**/.env.*`. Anything not excluded is sent to the builder and
can be copied into a layer.

**ENV-17 — Install dependencies in a cached, lockfile-first layer, then copy the
source.** Source edits then reuse the dependency layer.

- **Frontend.** Enable pnpm with `corepack enable` (NODE-2). Copy only the root
  `package.json` (for `packageManager`), `pnpm-workspace.yaml`, and `pnpm-lock.yaml`;
  `pnpm fetch` with a BuildKit cache mount; copy the source; install offline from the
  frozen lockfile; then build with one filter, `shared` first:
  `pnpm --filter "@app/frontend..." build`.
- **Backend.** Copy the `uv` binary from its pinned image, sync the locked dependencies
  with `pyproject.toml` and `uv.lock` bind-mounted, copy the source, then sync again to
  install the project itself (PY-3). The environment lives at `/opt/venv`
  (`UV_PROJECT_ENVIRONMENT`) and is first on `PATH`, so commands run without `uv run`.

```dockerfile
# syntax=docker/dockerfile:1
# check=error=true
ARG PYTHON_IMAGE=python:3.14.<patch>-slim-trixie@sha256:<digest>
ARG UV_IMAGE=ghcr.io/astral-sh/uv:<version>@sha256:<digest>

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS backend-base
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1
WORKDIR /app

FROM backend-base AS backend-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked
CMD ["fastapi", "dev", "api/app/main.py", "--host", "0.0.0.0"]

FROM backend-dev AS backend-test
CMD ["pytest", "-c", "pytest.ci.ini"]

FROM backend-base AS backend-build
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-install-project --no-dev
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev
# Smoke test: fail the build if the app cannot be imported without the dev group.
RUN python -c "import api.app.main"
```

`UV_PYTHON_DOWNLOADS=never` makes uv use the image's interpreter, so the Python version is
the one pinned by `PYTHON_IMAGE` and `.python-version` (PY-1). The `uv` image is pinned
like any other (ENV-24), since `COPY --from` cannot take an `ARG` directly.

**ENV-18 — Base images: pinned, Debian-based, and as small as the stage allows.**

- Frontend base, build, dev, and test stages use `node:24-bookworm` (NODE-1), which has
  the toolchain native addons need.
- Every backend stage uses `python:3.14-slim-trixie` at the exact version of PY-1. The
  locked dependencies install from wheels, so no compiler is needed. If one ever must
  build from source, give only `backend-build` the build packages, never `backend-prod`.
- Neither the Node nor the Python stages use `-alpine`: musl breaks prebuilt Node addons
  and many Python wheels. `frontend-prod` is the exception: it runs the official `caddy`
  image (ENV-22), a single static binary with no addons or wheels.

Declare each base image once, as an `ARG` before the first `FROM`.

**ENV-19 — Dev and test stages run the workspace's own tool directly.**

- The frontend's dev and test stages set `ENTRYPOINT ["pnpm", "frontend:base"]` and
  `CMD ["start:dev"]`, so `docker compose run frontend <script>` works for any script.
  The service sets `init: true`, because `pnpm` is PID 1.
- The backend's dev stage runs `fastapi dev` bound to `0.0.0.0` (FAPI-2), and its test
  stage runs `pytest -c pytest.ci.ini` (PYTEST-22). Neither sets an `ENTRYPOINT`, so
  `docker compose run --rm backend <command>` runs any command in the environment
  (`python -m scripts.seed_db`, `alembic heads`); the root `backend:run` script wraps it
  (MONO-11).

Dev and test stages MAY run as root.

**ENV-20 — A `-prod` stage contains only built output and production dependencies, and
runs as a non-root user.**

- `frontend-prod` follows ENV-22.
- `backend-prod` starts from the slim Python image again and copies `/opt/venv` and
  `/app` from `backend-build`, which synced without the `dev` group (ENV-17). It sets
  `ENVIRONMENT=prod` and `PYTHONDONTWRITEBYTECODE=1` (the source is read-only to the app
  user) only here, creates a system user, and listens above port 1024. Leave files
  root-owned unless the app writes to them.

**ENV-21 — `CMD` and `ENTRYPOINT` use exec form everywhere, and production runs the
server directly under a minimal init.** A shell wrapper can swallow `SIGTERM`. The image
SHOULD include `tini` or `dumb-init`; Compose `init: true` is acceptable while Compose is
the only runtime.

```dockerfile
FROM ${PYTHON_IMAGE} AS backend-prod
RUN apt-get update && apt-get install -y --no-install-recommends tini \
  && rm -rf /var/lib/apt/lists/* \
  && groupadd --system app && useradd --system --gid app --no-create-home app
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=prod
WORKDIR /app
COPY --from=backend-build /opt/venv /opt/venv
COPY --from=backend-build /app /app
USER app
EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "api.app.main:app", "--no-server-header"]
```

The same image runs migrations in production (`alembic upgrade head`, ALEM-13), as the
separate `backend-migrations` Railway service, which alone holds the owner role's
credentials ([github-actions.md](github-actions.md) GHA-27, GHA-28).

**ENV-22 — `frontend-prod` serves the Vite build with Caddy, and is production's public
entry point** (ENV-36), as in `aoam-property-plan`. The stage copies only
`frontend/dist` and `frontend/Caddyfile`, validates the Caddyfile at build time, and runs
as a non-root user on an unprivileged port. The image is pinned like any other, as
`ARG CADDY_IMAGE=caddy:<version>-alpine@sha256:<digest>` before the first `FROM`
(ENV-18, ENV-24). Never serve production traffic from `vite preview` or the dev server.

```dockerfile
FROM ${CADDY_IMAGE} AS frontend-prod
RUN addgroup -S app && adduser -S -G app app
# admin, persist_config, and auto_https are off, so Caddy writes nothing that matters here.
ENV XDG_CONFIG_HOME=/tmp/caddy-config XDG_DATA_HOME=/tmp/caddy-data
WORKDIR /srv
COPY frontend/Caddyfile ./Caddyfile
RUN caddy validate --config Caddyfile --adapter caddyfile
COPY --from=frontend-build /repo/frontend/dist ./dist
USER app
EXPOSE 8080
CMD ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]
```

The Caddyfile serves the build with a fallback to `index.html` for client-side routes, and
proxies the backend's paths to it over the private network, so the browser only ever
talks to one origin:

```caddyfile
{
	admin off # no admin API in production
	persist_config off # the filesystem is not persistent
	auto_https off # Railway terminates TLS
	log {
		format json
	}
	servers {
		trusted_proxies static private_ranges 100.0.0.0/8 # Railway's edge
	}
}

:{$PORT:8080} {
	log {
		format json
	}

	handle /api/* {
		reverse_proxy {$BACKEND_UPSTREAM:backend:8000}
	}

	handle /ws/* {
		reverse_proxy {$BACKEND_UPSTREAM:backend:8000}
	}

	handle {
		encode gzip
		root * dist
		try_files {path} /index.html
		file_server
	}
}
```

- `BACKEND_UPSTREAM` is `backend.railway.internal:8000` on Railway. Its default matches
  the Compose service name, so `caddy validate` passes at build time and the image also
  runs locally against the Compose network.
- Caddy's `reverse_proxy` passes WebSocket upgrades through and keeps them open, so `/ws/`
  needs no extra settings (compare ENV-37).
- Keep the Caddyfile formatted: `caddy fmt --overwrite frontend/Caddyfile` before
  committing.

---

## Image security and supply chain

**ENV-23 — Secrets never enter an image or its build history.** Never `COPY` `.env*`
files, `.npmrc` files with tokens, package-index credentials, keys, or certificates into
any stage, build stages included. Never pass a secret through `ARG` or `ENV`; both
persist, and CI provenance records build-arg values. A step that needs a credential
mounts it for that one `RUN`
(`RUN --mount=type=secret,id=npmrc,target=/root/.npmrc pnpm install …`). Keep tokens out
of the environment while `pnpm install` or `uv sync` runs; NODE-3 governs install
scripts.

**ENV-24 — Pin every image to an exact version, and let Dependabot update every pin.**
`FROM` lines, `ARG` image defaults, and Compose `image:` entries MUST name a full version
tag (`node:24.21.0-bookworm-slim`, `python:3.14.<patch>-slim-trixie`), never `latest`,
`lts`, or a bare major or minor, and SHOULD add the digest. A pin without automated
updates stops security fixes, so `.github/dependabot.yml` covers every ecosystem that
holds pins: `npm` (the pnpm lockfile), `uv` (`backend/uv.lock`), `docker` (every
directory with a Dockerfile, including `.github/tools/*`), `docker-compose`, and
`github-actions` (workflows and `.github/actions/*`). Updates run weekly, minor and patch
updates are grouped, and each update waits a 7-day cooldown after release. That is longer
than GitHub's 3-day default (since 14 July 2026), so a compromised release is more likely
to be pulled before it reaches this repository. Security updates ignore the cooldown.
Renovate MAY replace Dependabot.

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule: { interval: "weekly" }
    cooldown: { default-days: 7 }
    groups:
      npm-minor-and-patch: { update-types: ["minor", "patch"] }
  - package-ecosystem: "uv"
    directory: "/backend"
    schedule: { interval: "weekly" }
    cooldown: { default-days: 7 }
    groups:
      uv-minor-and-patch: { update-types: ["minor", "patch"] }
  - package-ecosystem: "github-actions"
    directories: ["/", "/.github/actions/*"]
    schedule: { interval: "weekly" }
    cooldown: { default-days: 7 }
    groups:
      actions-minor-and-patch: { update-types: ["minor", "patch"] }
  - package-ecosystem: "docker"
    directories: ["/backend", "/frontend", "/.github/tools/*"]
    schedule: { interval: "weekly" }
    cooldown: { default-days: 7 }
  - package-ecosystem: "docker-compose"
    directory: "/"
    schedule: { interval: "weekly" }
    cooldown: { default-days: 7 }
```

FastAPI's minor updates still get the one-at-a-time review of FAPI-22, even inside the
grouped PR.

**ENV-25 — Containers run with least privilege.** Never mount the Docker socket or use
`privileged: true`. Production services MUST set `cap_drop: [ALL]` and
`security_opt: ["no-new-privileges:true"]`, and SHOULD set `read_only: true` with a
`tmpfs` for `/tmp` (verify per image, especially `postgres`, which writes to its data
directory and `/var/run/postgresql`) and memory, CPU, and `pids` limits. Development
services SHOULD drop capabilities too unless a tool breaks. On a PaaS, use the platform's
equivalents.

**ENV-26 — CI scans images, and published images carry a GitHub attestation.**

- **Scanning.** The `docker` CI area scans each image it builds on a PR
  ([ci-pipeline.md](ci-pipeline.md) CI-13). `scan.yml` scans the published images
  weekly and uploads the results as SARIF to code scanning (free for public
  repositories; `security-events: write`). Use one free scanner. Trivy through
  `aquasecurity/trivy-action` MUST be pinned by SHA at v0.35.0 or later: on 19 March 2026,
  76 of 77 earlier tags were force-pushed to a credential stealer _(non-GitHub: Aqua
  Security, Microsoft)_. Grype or Docker Scout are alternatives. Fail on fixable `HIGH`
  and `CRITICAL` findings. Each accepted finding goes in the ignore file with a reason and
  an expiry date.
- **Attestation.** The `publish` job attests each pushed digest with GitHub's
  `actions/attest` (free for public repositories), in addition to
  `build-push-action`'s default provenance with `sbom: true`. That meets SLSA Build Level
  2. A deploy verifies it first:
  `gh attestation verify oci://docker.io/<user>/<image>:latest --repo <owner>/<repo>`
  ([github-actions.md](github-actions.md) GHA-27). An attestation shows where and how an
  image was built, not that it is safe.

Do not use Docker Content Trust; it shuts down on 2026-12-08.

---

## Build and CI

**ENV-27 — Pin every GitHub Action to a full commit SHA, with its version in a comment**
(`uses: docker/build-push-action@<sha> # v7.x.y`), and give each job the least
`permissions` it needs ([github-actions.md](github-actions.md) GHA-9, GHA-24). In March
2026 attackers force-pushed the tags of Trivy's actions to steal CI secrets. A job that
builds images gets no secret beyond its registry credential.

**ENV-28 — Production images are built only in CI**, by the `publish` job on pushes to
`main` and `v*` tags ([ci-pipeline.md](ci-pipeline.md) CI-13), and not by hand. The
one exception is the laptop fallback of ENV-41, for when CI cannot publish. PRs build
without pushing. CI uses Buildx through Docker's official
actions with the GitHub Actions cache (`type=gha`, `mode=max`) and one cache `scope` per
image, or each image's build overwrites the others' cache. Only pushing runs set
`cache-to`, so PR builds read `main`'s cache without evicting it. The cache backend has
required Buildx 0.21+ and BuildKit 0.20+ since 15 April 2025; current
`setup-buildx-action` releases provide them. Each image SHOULD be a target in a root
`docker-bake.hcl`, which records each image's context (ENV-14). Build for the deployment
target's platform; `linux/arm64` MAY use GitHub's arm64 runners, which are free for public
repositories.

**ENV-29 — CI runs checks the way developers do:** frontend and `shared` tests and every
static check (oxfmt, oxlint, Ruff, pyright) on the runner; backend tests in the
`backend-test` Compose service, against a real PostgreSQL
([python/pytest.md](python/pytest.md) PYTEST-10, PYTEST-22). Never test in a `-prod`
stage. [ci-pipeline.md](ci-pipeline.md) defines the jobs, and
[github-actions.md](github-actions.md) how workflows are written.

**ENV-30 — Images are published to Docker Hub from CI, and Railway deploys their
`:latest` tag.** This follows `aoam-property-plan`'s registry and host
([github-actions.md](github-actions.md) GHA-27, GHA-28), with the publishing moved from
`admin.sh docker publish` on a laptop into CI (ENV-28).

- **Repositories.** One Docker Hub repository per image:
  `<user>/msg-docking-bay-backend` and `<user>/msg-docking-bay-frontend`. Make them
  public, matching the GitHub repository, so Railway pulls without registry credentials.
- **Login.** The `publish` job logs in with the `DOCKERHUB_USERNAME` variable and the
  `DOCKERHUB_TOKEN` secret: a Docker Hub personal access token with **Read & Write**
  scope, never the account password and never an admin-scoped token. No other job
  receives it (GHA-9, GHA-26). Rotate it if it may have leaked, and when it expires.
- **Tags and labels.** `docker/metadata-action` tags every `main` build `sha-<short>`
  and `latest` (`type=raw,value=latest,enable={{is_default_branch}}`), and `vX.Y.Z` git
  tags `X.Y.Z`, and adds OCI labels, including `org.opencontainers.image.source`.
  `latest` therefore always means "the newest image that passed CI on `main`".
- **Deploys.** Railway services track `:latest`, and the `deploy` job redeploys them
  after each publish (GHA-27). Nothing else may push `latest`: no laptop pushes and no
  manual retagging. The `sha-<short>` tags are immutable and are the rollback targets;
  check whether the release being rolled back included a migration first (ALEM-13).
- **Cleanup.** Old `sha-` tags MAY be deleted, keeping at least the last ten for
  rollback.

---

## Production runtime

**ENV-31 — Production configuration comes from the runtime environment; secrets come from
files or the platform's secret store.** Use an untracked env file on a VPS or the
platform's settings on a PaaS. Secrets SHOULD be mounted files (Compose `secrets:`) or
platform secrets rather than plain env vars, which every process can read and logs can
leak. `EnvVars.from_environ` ([python/pydantic.md](python/pydantic.md) PYD-15) replaces
each `<NAME>_FILE` variable with the contents of that file before validating, so a secret
field such as `database_password` reads `DATABASE_PASSWORD_FILE` when it is set, and a
missing required secret still fails at startup.

**ENV-32 — Production runs on Railway (GHA-27); if it ever runs on Compose instead, it
uses an override file**
(`docker compose -f compose.yaml -f compose.production.yaml up -d`) that drops Watch and
bind mounts, runs the `-prod` images by SHA tag, publishes the proxy publicly, sets
`restart: unless-stopped`, and applies ENV-25. Never run the dev configuration in
production.

**ENV-33 — Containers shut down cleanly.** On `SIGTERM`, Uvicorn stops accepting
connections, waits for in-flight requests, and runs the app's lifespan shutdown (FAPI-1).
Bound that wait with `UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN`, and set the service's
`stop_grace_period` (the default is 10 s) above it, for example 20 s and `30s`. Uvicorn
closes open WebSocket connections as it stops; clients reconnect (WS-16), so a deploy MAY
drop WebSocket connections briefly.

**ENV-34 — Containers log to stdout and stderr only, and the host rotates logs.** Never
write log files inside a container (PY-38 configures stream handlers only). Docker's
default `json-file` driver does not rotate, so any Docker host we run MUST use
`logging: { driver: local }` or set `max-size` and `max-file` (for example `"10m"` and
`"3"`).

**ENV-35 — Production data is backed up, and the database is never publicly reachable.**
The database publishes no port, uses separate roles (ENV-13), and SHOULD sit on a network
the proxy cannot reach. Backups and restores follow [postgresql.md](postgresql.md) PG-22.

---

## Reverse proxy and TLS

**ENV-36 — Each environment has a single public entry point that routes by path:**

- `/api` → `backend` (the FastAPI app)
- `/ws/` → `backend` (FastAPI's WebSocket routes, served by the same Uvicorn process;
  [websockets.md](websockets.md))
- everything else → the frontend

In **development**, that entry point is the `proxy` Compose service (NGINX, ENV-37 to
ENV-39), which terminates TLS for `APP_DOMAIN` and routes "everything else" to the Vite
dev server. In **production on Railway**, it is the `frontend` service's Caddy (ENV-22):
Railway terminates TLS, the frontend is the only service with a public domain, and Caddy
proxies `/api` and `/ws/` to `backend.railway.internal` over Railway's private network.
The backend has no public domain, so nothing outside the project can reach it directly,
and the browser makes only same-origin requests: session cookies stay first-party, and
no build-time API URL is baked into the frontend.

On Railway the backend listens on `::` (`UVICORN_HOST=::`): private networks created
before 16 October 2025 resolve internal names to IPv6 only, and binding `::` accepts
both. The backend's `UVICORN_FORWARDED_ALLOW_IPS` names the proxy (FAPI-2), so client
addresses and the scheme come from the proxy's `X-Forwarded-*` headers and from nobody
else. On Railway it MAY be `*`, because only the private network can reach the backend.

**ENV-37 — The development proxy forwards WebSockets explicitly and keeps them open.** Set `Upgrade` and
`Connection` on the WebSocket location and on `/`, which carries Vite's HMR socket. NGINX
closes a connection after 60 s with no data, so raise `proxy_read_timeout` well above the
server's ping interval (Uvicorn pings every 20 s by default):

```nginx
map $http_upgrade $connection_upgrade { default upgrade; '' close; }

location /ws/ {
  proxy_pass http://backend;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection $connection_upgrade;
  proxy_read_timeout 1h;
}
```

**ENV-38 — The development proxy SHOULD run as `nginxinc/nginx-unprivileged`**, listening on 8080 and
8443 inside the container, so it can run under ENV-25. Set `server_tokens off;`, allow only
TLS 1.2 and 1.3, and mount certificates read-only.

**ENV-39 — TLS certificates are generated or renewed by tooling, never committed.**
Locally, a setup script runs `mkcert` into a git-ignored `certs/` directory. Never mount
mkcert's `rootCA-key.pem`; a Node container that calls the proxy over HTTPS gets
`NODE_EXTRA_CA_CERTS` pointing at `rootCA.pem`. The backend calls other services by
Compose service name, not through the proxy. In production, a PaaS terminates TLS, or the
VPS edge renews via ACME (certbot or Caddy). Never renew certificates by hand.

**ENV-40 — Frontend and backend code MUST NOT hard-code `localhost` URLs or ports.**
Derive them from configuration (`APP_DOMAIN`, `window.location`, `EnvVars`) and route
traffic through the proxy. The Vite dev server sets `server.host: true`,
`server.strictPort: true`, and `server.allowedHosts: [APP_DOMAIN]`, never
`allowedHosts: true`. The backend's CORS and trusted-host lists are built from
`APP_DOMAIN` (FAPI-17).

---

## Manual publishing fallback

**ENV-41 — When CI cannot publish, the owner MAY publish from a laptop with
`pnpm docker:publish`.** It is a fallback, not a second pipeline: use it only when the
`publish` job cannot run (a GitHub Actions outage, a broken runner image), and let the
next successful CI publish replace what it pushed. The root script runs
`scripts/publish-images.sh`, which follows `aoam-property-plan`'s
`admin.sh docker publish` with these guards:

- **Only what CI would have shipped.** It refuses to run unless the working tree is clean
  and `HEAD` equals `origin/main` after a `git fetch`, and unless `ci-success` passed for
  that commit (`gh api repos/<owner>/<repo>/commits/<sha>/check-runs`). `--without-ci`
  skips the last check, for when Actions itself is down, and prints a warning.
- **Credentials from 1Password, never from disk.** It reads the Docker Hub username and
  a Read & Write access token with `op read` from the paths in `DOCKER_USERNAME_OP_PATH`
  and `DOCKER_TOKEN_OP_PATH`, logs in with `docker login --password-stdin`, and runs
  `docker logout` on exit (a `trap`), so no token is left in `~/.docker/config.json`.
- **The same images CI builds.** It builds the `docker-bake.hcl` targets (ENV-28) for
  `linux/amd64`, Railway's platform, which an Apple Silicon laptop would not build by
  default. It pushes the same `sha-<short>` and `latest` tags as CI (ENV-30), with
  Buildx's own provenance and SBOM attestations (`--provenance=true --sbom=true`).
- **No GitHub attestation.** A laptop cannot create one, so the `deploy` job's
  verification (GHA-27) would reject these images. Deploy them by hand, in the same order
  as the `deploy` job: `railway redeploy --service backend-migrations`, wait for it to
  finish, then `backend`, then `frontend`, logged in with `railway login`.

Record each use in the PR or issue that explains why CI could not publish.

