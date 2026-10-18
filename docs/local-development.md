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
  loaded on top of it for tests. Passwords are files in `.docker/secrets/`, mounted as
  Compose secrets, and read through `*_FILE` variables. `.docker/` and
  `nginx-reverse-proxy/certs/` are git-ignored.
- **Database roles.** On a fresh volume, `postgres/initdb/` creates `app_owner`
  (owns the schema, runs migrations) and `app` (reads and writes rows; the backend's
  role). To start over: `docker compose down -v`.
- **Proxy.** `nginx-reverse-proxy/templates/default.conf.template` routes `/api` and `/ws/` to the
  backend and everything else, including Vite's HMR socket, to the frontend.
- **Versions.** `.prototools` pins every tool. `frontend/.nvmrc` and
  `backend/.python-version` repeat the Node and Python pins and must stay equal.
- **Production images** are not built yet; see
  [decisions/0001-production-image-build.md](decisions/0001-production-image-build.md).
