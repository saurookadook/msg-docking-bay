# syntax=docker/dockerfile:1
# check=error=true

# Production stages follow ENV-17, not moon's MDOCK-1:
# docs/decisions/0001-production-image-build.md.

ARG PYTHON_IMAGE=python:3.14.8-slim-trixie@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336

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
# `fastapi dev` ignores UVICORN_* variables but reads its port from PORT, which Compose
# sets from UVICORN_PORT so the server, healthcheck, and proxy agree (ENV-19).
ENV PORT=8000
EXPOSE 8000
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

FROM ${PYTHON_IMAGE} AS backend-prod
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --no-create-home app
# Uvicorn reads UVICORN_* variables. These defaults let the image run as is; Railway
# sets UVICORN_HOST=:: (ENV-36).
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=prod \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000
WORKDIR /app
COPY --from=backend-build /opt/venv /opt/venv
COPY --from=backend-build /app /app
USER app
EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "api.app.main:app", "--no-server-header"]
