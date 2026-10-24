# syntax=docker/dockerfile:1
# check=error=true

# The database image, published and run by compose.yaml: PostgreSQL with postgres/initdb/
# baked in, so a fresh data folder gets the roles of PG-13 without a bind mount. The init
# scripts read the role passwords from /run/secrets (db_owner_password, db_app_password);
# whatever runs the image must provide them.

ARG POSTGRES_IMAGE=postgres:18.6-trixie@sha256:74935e72241653ca55e0414067e6d8763aceb8a810eb51b452253ec3dcfc4336

FROM ${POSTGRES_IMAGE} AS postgres-prod
COPY --chmod=0755 initdb/ /docker-entrypoint-initdb.d/
