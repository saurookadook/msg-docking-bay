# syntax=docker/dockerfile:1
# check=error=true

# The backend is a path dependency (`../backend`), so it arrives as the named build
# context `backend` (Compose `additional_contexts`, or `--build-context
# backend=backend`) and sits beside this project, at /app/backend, in every stage.
# Production stages follow ENV-17, as backend/Dockerfile does.

# The same pins as backend/Dockerfile; upgrade both together (PY-1, ENV-24).
ARG PYTHON_IMAGE=python:3.14.8-slim-trixie@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS ingest-base
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1
WORKDIR /app/ingest

FROM ingest-base AS ingest-dev
# The backend is bind-mounted, not copied, for the dependency layer: uv reads its
# metadata and records the editable install, and the layer is rebuilt only when
# ingest's lockfile changes, not on every backend edit.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,from=backend,target=/app/backend,rw \
    uv sync --locked --no-install-project
COPY --from=backend . /app/backend
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked
CMD ["python", "-m", "ingest", "--help"]

FROM ingest-dev AS ingest-test
CMD ["pytest", "-c", "pytest.ci.ini"]

FROM ingest-base AS ingest-build
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,from=backend,target=/app/backend,rw \
    uv sync --locked --no-install-project --no-dev
COPY --from=backend . /app/backend
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev
# Smoke test: fail the build if the CLI cannot be imported without the dev group.
RUN python -c "import ingest.cli"

FROM ${PYTHON_IMAGE} AS ingest-prod
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --no-create-home app
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=prod
WORKDIR /app/ingest
COPY --from=ingest-build /opt/venv /opt/venv
COPY --from=ingest-build /app /app
USER app
ENTRYPOINT ["/usr/bin/tini", "--", "python", "-m", "ingest"]
CMD ["--help"]
