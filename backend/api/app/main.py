"""Build the FastAPI application (FAPI-1)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from api.models.health_check import HealthCheckResponse, HealthCheckStatus
from api.routes.home import home_router
from utils.logging.init import init_logging

logger = init_logging(app_name="msg-docking-bay-api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Log the server's start and shutdown."""
    logger.info("Starting API server...")
    yield
    logger.info("Shutting down API server...")


def operation_id_from_route_name(route: APIRoute) -> str:
    """Use the route function's name as its OpenAPI operation ID.

    FastAPI's default appends the path and method
    (``read_home_api_get``), and generated clients use the operation
    ID as the method name (FAPI-6). Route names must therefore be
    unique across the app; FastAPI warns on a duplicate ID.
    """
    return route.name


app = FastAPI(
    generate_unique_id_function=operation_id_from_route_name, lifespan=lifespan
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return a 422 without echoing input, context, or library links."""
    errors: list[dict[str, object]] = [
        {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]
    logger.info(
        "Rejected %s %s: %s",
        request.method,
        request.url.path,
        [(error["loc"], error["type"]) for error in errors],
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": errors}
    )


@app.get("/api/health-check")
def read_health_check() -> HealthCheckResponse:
    """Report that the process is up.

    Touches nothing else (no database, no upstream call), so platform
    health checks stay cheap (FAPI-3).
    """
    return HealthCheckResponse(data=HealthCheckStatus(status="ok"))


app.include_router(home_router)
