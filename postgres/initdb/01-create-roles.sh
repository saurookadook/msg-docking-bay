#!/usr/bin/env bash
# Create the owner and application roles of PG-13 on a fresh local data folder (PG-19).
# The postgres image runs this once, as the superuser, only while the data folder is
# empty. Extensions and schema belong in migrations (PG-12), not here.
#
# Reads: POSTGRES_DB, DATABASE_OWNER_USER, DATABASE_USER, and the password files that
# the secrets-init service copies into /run/secrets for the postgres user.
set -euo pipefail

owner_password="$(< /run/secrets/db_owner_password)"
app_password="$(< /run/secrets/db_app_password)"

psql --variable=ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=db="$POSTGRES_DB" \
  --set=owner="$DATABASE_OWNER_USER" \
  --set=owner_password="$owner_password" \
  --set=app="$DATABASE_USER" \
  --set=app_password="$app_password" <<'SQL'
CREATE ROLE :"owner" LOGIN PASSWORD :'owner_password';
CREATE ROLE :"app" LOGIN PASSWORD :'app_password';

-- Since PostgreSQL 15, the database owner also owns the `public` schema.
ALTER DATABASE :"db" OWNER TO :"owner";
ALTER SCHEMA public OWNER TO :"owner";
REVOKE ALL ON DATABASE :"db" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"db" TO :"app";
GRANT USAGE ON SCHEMA public TO :"app";

-- Tables and sequences that later migrations create (as the owner) are covered too.
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :"app";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO :"app";
SQL
