import logging

import pytest
from fastapi import HTTPException, status

from api.routes.handlers.reads import run_read

logger = logging.getLogger(__name__)


class MissingError(Exception):
    pass


def fail(error: Exception) -> str:
    raise error


class TestRunRead:
    def test_returns_the_result(self) -> None:
        assert run_read(lambda: "ok", error_detail="Error", logger=logger) == "ok"

    def test_maps_not_found_to_404(self) -> None:
        with pytest.raises(HTTPException) as caught:
            run_read(
                lambda: fail(MissingError("no row")),
                error_detail="Error fetching thing",
                logger=logger,
                not_found=MissingError,
                not_found_detail="Thing not found",
            )

        assert caught.value.status_code == status.HTTP_404_NOT_FOUND
        assert caught.value.detail == "Thing not found"
        assert isinstance(caught.value.__cause__, MissingError)

    def test_maps_anything_else_to_a_logged_500(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """The client gets the fixed detail; the log gets the error."""
        with pytest.raises(HTTPException) as caught:
            run_read(
                lambda: fail(RuntimeError("password=hunter2")),
                error_detail="Error fetching thing",
                logger=logger,
                not_found=MissingError,
            )

        assert caught.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert caught.value.detail == "Error fetching thing"
        assert "hunter2" in caplog.text

    def test_without_not_found_every_error_is_a_500(self) -> None:
        """A list route passes no ``not_found``, so it has no 404."""
        with pytest.raises(HTTPException) as caught:
            run_read(lambda: fail(MissingError()), error_detail="Error", logger=logger)

        assert caught.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
