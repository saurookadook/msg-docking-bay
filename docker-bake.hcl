# The production images and their build contexts (ENV-14, ENV-28). Pushed by
# scripts/publish-images.sh (`moon run <project>:publish`); see docs/local-development.md.
#
# Name the file: a bare `docker buildx bake` also reads compose.yaml and merges its
# same-named services into these targets.
#
#   DOCKER_USERNAME=<user> GIT_SHA=$(git rev-parse --short HEAD) docker buildx bake --file docker-bake.hcl

variable "DOCKER_USERNAME" {
  default = "local"
}

# The short commit SHA. Every image is tagged `sha-<GIT_SHA>` and `latest`, which Railway
# deploys (ENV-30).
variable "GIT_SHA" {
  default = "unknown"
}

function "tags" {
  params = [name]
  result = [
    "${DOCKER_USERNAME}/msg-docking-bay-${name}:sha-${GIT_SHA}",
    "${DOCKER_USERNAME}/msg-docking-bay-${name}:latest",
  ]
}

group "default" {
  targets = ["backend", "frontend", "postgres"]
}

target "_common" {
  # Railway's platform, which an Apple Silicon laptop would not build by default.
  platforms = ["linux/amd64"]
  labels = {
    "org.opencontainers.image.source"   = "https://github.com/saurookadook/msg-docking-bay"
    "org.opencontainers.image.revision" = GIT_SHA
  }
}

target "backend" {
  inherits = ["_common"]
  context  = "backend"
  target   = "backend-prod"
  tags     = tags("backend")
}

# frontend/ is the pnpm root, so it is the context, not the repository root (ENV-14).
target "frontend" {
  inherits = ["_common"]
  context  = "frontend"
  target   = "frontend-prod"
  tags     = tags("frontend")
}

target "postgres" {
  inherits = ["_common"]
  context  = "postgres"
  target   = "postgres-prod"
  tags     = tags("postgres")
}
