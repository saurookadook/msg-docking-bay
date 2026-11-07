from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from _factories.ingest_run.db import IngestRunDBFactory
from _fixtures.environment import TEST_DATABASE_NAME
from models.ingest_run.db import IngestRunDB


class TestBackendReuse:
    """The ingest suite runs on the backend's test setup, not a copy."""

    def test_connects_to_the_migrated_test_database(
        self, test_db_session: Session
    ) -> None:
        database = test_db_session.execute(text("SELECT current_database()"))

        assert database.scalar_one() == TEST_DATABASE_NAME
        assert test_db_session.execute(
            text("SELECT to_regclass('ingest_runs') IS NOT NULL")
        ).scalar_one()

    def test_builds_rows_with_the_backend_factories(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        IngestRunDBFactory()
        test_db_session.commit()

        runs = test_db_session.execute(
            select(func.count()).select_from(IngestRunDB)
        ).scalar_one()
        started_at = test_db_session.execute(
            select(IngestRunDB.started_at)
        ).scalar_one()

        assert runs == 1
        assert started_at == mock_utcnow
