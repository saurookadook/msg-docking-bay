#!/usr/bin/env bash
# Run the backend test suite in its own Compose project, against a throwaway PostgreSQL
# database, then remove that project's containers and volumes (ENV-4, PG-17). Arguments,
# if any, replace the service's command: `scripts/backend-test.sh pytest -k env_vars`.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

compose=(
  docker compose
  --project-name msg-docking-bay-test
  --file compose.yaml
  --file compose.test.yaml
  --env-file .env
  --env-file .env.test
)

cleanup() { "${compose[@]}" --profile test down --volumes --remove-orphans; }
trap cleanup EXIT

"${compose[@]}" run --rm --build backend-test "$@"
