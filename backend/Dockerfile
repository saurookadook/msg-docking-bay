# syntax=docker/dockerfile:1
# check=error=true

# Development and test stages only. How production images are built is an open
# decision: docs/decisions/0001-production-image-build.md.

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
EXPOSE 8000
# `fastapi dev` does not read UVICORN_* variables, so the port is given here; keep it
# equal to UVICORN_PORT, which the healthcheck and the proxy use.
CMD ["fastapi", "dev", "api/app/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM backend-dev AS backend-test
CMD ["pytest", "-c", "pytest.ci.ini"]
