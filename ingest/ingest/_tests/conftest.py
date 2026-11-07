"""Fixtures for the ingest package's tests (PYTEST-9)."""

from collections.abc import Callable, Iterator

import pytest
from sqlalchemy import Connection, delete, select
from sqlalchemy.orm import Session, sessionmaker

from constants.catalog import IngestRunStatus
from db.db_session_manager import DBSessionManager
from ingest.runs import SessionFactory
from models.ingest_run.db import IngestRunDB


@pytest.fixture
def run_sessions(test_db_session: Session) -> SessionFactory:
    """Open sessions on the test connection; commits are savepoints.

    Code under test opens its own sessions from a factory, as it does
    in production, and the test's rollback still removes their work.
    """
    return sessionmaker(
        bind=test_db_session.connection(), join_transaction_mode="create_savepoint"
    )


@pytest.fixture
def test_connection(test_db_session: Session) -> Connection:
    """Return the test's rolled-back connection, for a run to lock.

    Commits on it become savepoints, so a run's writes vanish with the
    test like everything else.
    """
    return test_db_session.connection()


type CommittedStatuses = Callable[[], list[tuple[IngestRunStatus, str | None]]]


@pytest.fixture
def committed_runs() -> Iterator[CommittedStatuses]:
    """Yield a reader of committed runs, and delete them afterwards.

    A run on its own connection commits for real, outside the test's
    rollback; the reader sees those rows, oldest first, and they are
    deleted when the test ends.
    """

    def statuses() -> list[tuple[IngestRunStatus, str | None]]:
        with DBSessionManager().engine.connect() as connection:
            return [
                (status, summary)
                for status, summary in connection.execute(
                    select(IngestRunDB.status, IngestRunDB.error_summary).order_by(
                        IngestRunDB.started_at, IngestRunDB.id
                    )
                )
            ]

    yield statuses
    with DBSessionManager().engine.begin() as connection:
        connection.execute(delete(IngestRunDB))
