"""Test-database fixtures shared by every suite that uses the catalog.

A root ``conftest.py`` calls ``use_test_database()`` from
``_fixtures.environment`` first, then loads this module with
``pytest_plugins = ["_fixtures.db"]``. The backend and ingest suites
both do, so they migrate and isolate the database the same way
(PYTEST-10).
"""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Final

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from _mocks.temporal import get_mock_utcnow
from db.db_session_manager import DBSessionManager

ALEMBIC_INI: Final = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    """Load the backend's Alembic configuration, from any directory."""
    return Config(str(ALEMBIC_INI))


def pytest_sessionstart(session: pytest.Session) -> None:
    """Migrate the test database once, before any test (ALEM-13)."""
    command.upgrade(alembic_config(), "head")


@pytest.fixture(autouse=True)
def test_db_session() -> Iterator[Session]:
    """Yield a session whose work is rolled back after the test.

    Commits inside the test release savepoints, so code that commits
    runs unchanged.
    """
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
def mock_utcnow() -> datetime:
    """Return the suite's fixed "now" (PYTEST-18)."""
    return get_mock_utcnow()
