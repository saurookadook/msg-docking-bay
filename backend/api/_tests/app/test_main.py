import asyncio
import json

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError

from api.app.main import app, validation_error_handler


class TestValidationErrorHandler:
    def test_keeps_only_loc_msg_and_type(self) -> None:
        """The submitted value, context, and docs link must not leak
        (FAPI-23).
        """
        exc = RequestValidationError(
            [
                {
                    "ctx": {"secret_ctx": "internal"},
                    "input": "hunter2",
                    "loc": ("body", "password"),
                    "msg": "String should have at least 12 characters",
                    "type": "string_too_short",
                    "url": "https://errors.pydantic.dev/",
                }
            ]
        )
        request = Request(
            {"headers": [], "method": "POST", "path": "/api", "type": "http"}
        )

        response = asyncio.run(validation_error_handler(request, exc))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert json.loads(bytes(response.body)) == {
            "detail": [
                {
                    "loc": ["body", "password"],
                    "msg": "String should have at least 12 characters",
                    "type": "string_too_short",
                }
            ]
        }


class TestOperationIds:
    def test_match_the_route_function_names(self) -> None:
        operation_ids = {
            path: [operation["operationId"] for operation in methods.values()]
            for path, methods in app.openapi()["paths"].items()
        }

        assert operation_ids == {
            "/api": ["read_home"],
            "/api/health-check": ["read_health_check"],
        }
