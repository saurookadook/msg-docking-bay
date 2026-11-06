"""Root fixtures shared by every test package (PYTEST-9)."""

import os
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from _mocks.temporal import get_mock_utcnow
from config.env_vars import EnvVarManager

# Set before the app is imported, since importing it configures logging
# from the environment (PYTEST-10).
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_NAME"] = "test_msg_docking_bay"
EnvVarManager().reload()  # the frozen EnvVars is re-validated, never assigned to

# These must follow the environment setup above.
from api.app.main import app  # noqa: E402
from api.dependencies.db_session import api_db_session  # noqa: E402
from db.db_session_manager import DBSessionManager  # noqa: E402

ALEMBIC_INI = Path(__file__).parent / "alembic.ini"


def alembic_config() -> Config:
    """Load the project's Alembic configuration."""
    return Config(str(ALEMBIC_INI))


def pytest_sessionstart(session: pytest.Session) -> None:
    """Migrate the test database once, before any test (ALEM-13)."""
    command.upgrade(alembic_config(), "head")


@pytest.fixture(autouse=True)
def test_db_session() -> Iterator[Session]:
    db_session_manager = DBSessionManager()
    scoped = db_session_manager.scoped_session

    with (
        db_session_manager.engine.connect() as db_connection,
        db_connection.begin() as transaction,
    ):
        try:
            yield scoped(bind=db_connection, join_transaction_mode="create_savepoint")
        finally:
            scoped.remove()
            transaction.rollback()


@pytest.fixture
def test_app_client(test_db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[api_db_session] = lambda: test_db_session
    try:
        yield TestClient(app, base_url="https://app.dev")
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_utcnow() -> datetime:
    """Return the suite's fixed "now" (PYTEST-18)."""
    return get_mock_utcnow()
