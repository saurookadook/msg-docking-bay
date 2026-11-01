#!/usr/bin/env bash
# Build the production images in docker-bake.hcl and push them to Docker Hub (ENV-41).
# Arguments name the bake targets (backend, frontend, postgres); none means all three:
# `scripts/publish-images.sh backend`.
#
# Credentials come from 1Password: DOCKER_USERNAME_OP_PATH and DOCKER_TOKEN_OP_PATH
# (or DOCKER_PASSWORD_OP_PATH) hold `op://` references, read with `op read`. The login
# goes into a throwaway DOCKER_CONFIG, deleted on exit, so no token is left on disk and
# Docker Desktop's own sign-in, which shares ~/.docker's credential store, is untouched.
#
# Every image is tagged `latest` and `sha-<short>`; a dirty tree's SHA tag gets a `-dirty`
# suffix. The git and CI checks of ENV-41 are not here yet.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

token_op_path="${DOCKER_TOKEN_OP_PATH:-${DOCKER_PASSWORD_OP_PATH:-}}"
if [[ -z "${DOCKER_USERNAME_OP_PATH:-}" || -z "$token_op_path" ]]; then
  echo "Set DOCKER_USERNAME_OP_PATH and DOCKER_TOKEN_OP_PATH to op:// references." >&2
  exit 1
fi

git_sha="$(git rev-parse --short HEAD)"
if [[ -n "$(git status --porcelain)" ]]; then
  git_sha="${git_sha}-dirty"
  echo "The working tree has changes: tagging latest and sha-${git_sha}." >&2
fi

# Docker Desktop's default `docker` driver cannot attach provenance or SBOM attestations
# unless the containerd image store is on, so build with a docker-container builder.
builder=msg-docking-bay-publish
if ! docker buildx inspect "$builder" >/dev/null 2>&1; then
  docker buildx create --name "$builder" --driver docker-container >/dev/null
fi

# A `docker logout` would sign Docker Desktop out too, so log in to a config of our own. It
# links the real contexts, builders, and CLI plugins, and keeps the current context.
user_docker_config="${DOCKER_CONFIG:-$HOME/.docker}"
docker_context="$(docker context show)"
DOCKER_CONFIG="$(mktemp -d)"
export DOCKER_CONFIG
trap 'rm -rf "$DOCKER_CONFIG"' EXIT
for dir in contexts buildx cli-plugins; do
  if [[ -d "$user_docker_config/$dir" ]]; then
    ln -s "$user_docker_config/$dir" "$DOCKER_CONFIG/$dir"
  fi
done
# Without an `auths` entry the CLI falls back to the platform's credential helper (the
# macOS keychain) and would overwrite Docker Desktop's Hub login there. The empty entry
# keeps the login in this config file, which the trap deletes.
printf '{"currentContext": "%s", "auths": {"https://index.docker.io/v1/": {}}}\n' "$docker_context" >"$DOCKER_CONFIG/config.json"

docker_username="$(op read "$DOCKER_USERNAME_OP_PATH")"
op read "$token_op_path" | docker login --username "$docker_username" --password-stdin

DOCKER_USERNAME="$docker_username" GIT_SHA="$git_sha" \
  docker buildx bake --builder "$builder" --file docker-bake.hcl --push --provenance=true --sbom=true "$@"
