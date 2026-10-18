"""Root fixtures shared by every test package (PYTEST-9)."""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from config.env_vars import EnvVarManager

# Set before the app is imported, since importing it configures logging
# from the environment (PYTEST-10).
os.environ["ENVIRONMENT"] = "test"
EnvVarManager().reload()  # the frozen EnvVars is re-validated, never assigned to

from api.app.main import app  # noqa: E402 - must follow the environment setup above


@pytest.fixture
def test_app_client() -> Iterator[TestClient]:
    # TODO: override ``api_db_session`` with ``test_db_session`` here
    # once the database lands (PYTEST-14).
    with TestClient(app, base_url="https://app.dev") as client:
        yield client
