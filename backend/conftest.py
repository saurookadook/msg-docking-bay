"""Root fixtures shared by every test package (PYTEST-9)."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from _fixtures.environment import use_test_database

# Set before the app is imported, since importing it configures logging
# from the environment (PYTEST-10).
use_test_database()

# These must follow the environment setup above.
from api.app.main import app  # noqa: E402
from api.dependencies.db_session import api_db_session  # noqa: E402

# The migration at session start, test_db_session and mock_utcnow; the
# ingest suite loads the same module.
pytest_plugins = ["_fixtures.db"]


@pytest.fixture
def test_app_client(test_db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[api_db_session] = lambda: test_db_session
    try:
        yield TestClient(app, base_url="https://app.dev")
    finally:
        app.dependency_overrides.clear()
