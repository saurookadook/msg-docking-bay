# Local development

The whole stack runs in Docker Compose behind an NGINX proxy at
**https://msg-docking-bay.dev**. moon runs every task, on the host or in Compose.

| Service    | What it is                                    | Reached at                              |
| ---------- | --------------------------------------------- | --------------------------------------- |
| `proxy`    | NGINX, TLS for `APP_DOMAIN`                   | `https://msg-docking-bay.dev`            |
| `frontend` | Vite dev server                               | everything except `/api` and `/ws/`     |
| `backend`  | FastAPI (`fastapi dev`)                       | `/api`, `/ws/`                          |
| `postgres` | PostgreSQL 18, data in the `postgres-data` volume | the Compose network only            |
| `all`      | a no-op that depends on the stack, so `docker compose up all` starts it in order | — |

## First-time setup

1. Install [Docker Desktop](https://docs.docker.com/desktop/) (Compose 2.33.1 or later)
   and [mkcert](https://github.com/FiloSottile/mkcert).
2. Install proto, then the pinned tools from `.prototools` (moon, Node, pnpm, Python, uv):

   ```sh
   curl -fsSL https://moonrepo.dev/install/proto.sh | bash
   proto install
   ```

3. Generate moon's config schemas and install the pre-commit hook (`.moon/cache` is not
   committed, and hooks are installed per developer):

   ```sh
   moon sync config-schemas
   moon sync vcs-hooks
   ```

4. Create `.env`, `.env.test`, TLS certificates, and the database passwords:

   ```sh
   moon run root:setup
   ```

   It never overwrites existing files. If it reports that the domain is missing from
   `/etc/hosts`, add it (`.dev` is a real top-level domain, so nothing else resolves it
   to your machine):

   ```sh
   sudo sh -c 'echo "127.0.0.1 msg-docking-bay.dev" >> /etc/hosts'
   ```

5. The proxy publishes `PROXY_HTTP_PORT` and `PROXY_HTTPS_PORT` (80 and 443 in
   `.env.example`) on `PROXY_BIND_ADDRESS` (127.0.0.1). Docker Desktop binds ports below
   1024 on 127.0.0.1 only with **Settings → Advanced → Allow privileged port mapping**
   turned on. Without it, either:
   - set the ports to free ones above 1024 in `.env` (for example 8080 and 8443) and open
     `https://msg-docking-bay.dev:8443`, or
   - set `PROXY_BIND_ADDRESS=0.0.0.0`, which works without the setting but opens the
     stack to your network (ENV-12).

6. Start the stack, then apply migrations:

   ```sh
   moon run root:dev          # docker compose up --build --watch --attach-dependencies all
   moon run backend:migrate   # in another terminal
   ```

## Daily commands

| Command                                  | Does                                                        |
| ---------------------------------------- | ----------------------------------------------------------- |
| `moon run root:dev`                      | start the stack through the `all` service; source changes sync into the containers. Ctrl-C stops only `all` |
| `moon run root:down`                     | stop and remove the stack (data stays in the volume)        |
| `moon run :format :lint :typecheck`      | every static check, on the host                             |
| `moon run frontend:test`                 | Vitest                                                      |
| `moon run backend:test`                  | pytest against a throwaway database, in its own Compose project |
| `moon run backend:migrate`               | `alembic upgrade head`, as the owner role                   |
| `docker compose run --rm backend-migrations revision --autogenerate -m "..."` | new migration |
| `docker compose run --rm backend <cmd>`  | any command in the backend's image (rebuild it first: Watch only syncs the running container) |
| `moon run :format-write :lint-fix`       | fix formatting and autofixable lint                         |

## How it fits together

- **Configuration.** `.env` (from `.env.example`) feeds every service; `.env.test` is
  loaded on top of it for tests. Passwords are files in `.docker/secrets/`, read
  through `*_FILE` variables. `.docker/` and `nginx-reverse-proxy/certs/` are
  git-ignored.
- **Secrets and the TLS key.** The setup script writes them readable only by you. On
  every `up`, the short-lived `secrets-init` service copies them into volumes owned by
  the container users that read them: the proxy's key and the database passwords. The
  backend services run as root and mount the passwords as Compose secrets. After
  regenerating a file, the next `up` picks it up.
- **Database roles.** On a fresh volume, `postgres/initdb/` creates the two roles named
  in `.env`: `DATABASE_OWNER_USER` (owns the schema, runs migrations) and `DATABASE_USER`
  (reads and writes rows; the backend's role). To start over: `docker compose down -v`.
- **Proxy.** `nginx-reverse-proxy/templates/default.conf.template` routes `/api` and `/ws/` to the
  backend and everything else, including Vite's HMR socket, to the frontend.
- **Versions.** `.prototools` pins every tool. `frontend/.nvmrc` and
  `backend/.python-version` repeat the Node and Python pins and must stay equal.
- **Production images** are the `-prod` stages of `backend/Dockerfile`,
  `frontend/Dockerfile` (Caddy, `frontend/Caddyfile`), and `postgres/Dockerfile`, listed
  in `docker-bake.hcl`; see
  [decisions/0001-production-image-build.md](decisions/0001-production-image-build.md).

## Publishing images

CI does not publish yet, so images are pushed from a laptop with the ENV-41 fallback
script, `scripts/publish-images.sh`:

| Command                     | Pushes                                     |
| --------------------------- | ------------------------------------------ |
| `moon run root:publish`     | all three images, in one login             |
| `moon run backend:publish`  | `<user>/msg-docking-bay-backend`           |
| `moon run frontend:publish` | `<user>/msg-docking-bay-frontend`          |
| `moon run postgres:publish` | `<user>/msg-docking-bay-postgres`          |

- **Credentials.** Export `DOCKER_USERNAME_OP_PATH` and `DOCKER_TOKEN_OP_PATH` (or
  `DOCKER_PASSWORD_OP_PATH`) as `op://` references to your Docker Hub username and a
  Read & Write access token, and sign in to the 1Password CLI. The script logs in with
  `docker login --password-stdin` to a throwaway Docker config, deleted when it exits,
  so Docker Desktop stays signed in.
- **Tags.** Every image is built for `linux/amd64` and tagged `latest`, which Railway
  deploys (ENV-30), and `sha-<short>`; with uncommitted changes the SHA tag is
  `sha-<short>-dirty`.
- **Not yet checked.** The script does not fetch `origin/main` or check CI (ENV-41), so
  make sure what you push is what you mean to ship.
