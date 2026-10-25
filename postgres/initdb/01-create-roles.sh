#!/usr/bin/env bash
# Create the owner and application roles of PG-13 on a fresh local data folder (PG-19).
# The postgres image runs this once, as the superuser, only while the data folder is
# empty. Extensions and schema belong in migrations (PG-12), not here.
#
# Reads: POSTGRES_DB, DATABASE_OWNER_USER, DATABASE_USER, and each role's password
# from DATABASE_OWNER_PASSWORD and DATABASE_APP_PASSWORD (Railway's variables) or, when
# unset, from the files that the secrets-init service copies into /run/secrets for the
# postgres user (Compose).
set -euo pipefail

# Print the variable named $1 if it is set, else the contents of the file $2.
read_password() {
  local name="$1" file="$2"
  if [[ -n "${!name:-}" ]]; then
    printf '%s' "${!name}"
  elif [[ -r "$file" ]]; then
    printf '%s' "$(< "$file")"
  else
    echo "$0: set $name or provide $file" >&2
    return 1
  fi
}

owner_password="$(read_password DATABASE_OWNER_PASSWORD /run/secrets/db_owner_password)"
app_password="$(read_password DATABASE_APP_PASSWORD /run/secrets/db_app_password)"

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
