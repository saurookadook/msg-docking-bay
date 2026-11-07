"""Fixtures for the ingest package's tests (PYTEST-9)."""

import pytest
from sqlalchemy.orm import Session, sessionmaker

from ingest.runs import SessionFactory


@pytest.fixture
def run_sessions(test_db_session: Session) -> SessionFactory:
    """Open sessions on the test connection; commits are savepoints.

    Code under test opens its own sessions from a factory, as it does
    in production, and the test's rollback still removes their work.
    """
    return sessionmaker(
        bind=test_db_session.connection(), join_transaction_mode="create_savepoint"
    )
