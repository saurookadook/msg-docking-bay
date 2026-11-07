import pytest
from sqlalchemy import Connection, func, select
from sqlalchemy.orm import Session

from _mocks.temporal import get_mock_utcnow
from constants.catalog import ContentLicense, IngestRunStatus, SourceKind
from ingest._tests.conftest import CommittedStatuses
from ingest.errors import SchemaNotAtHeadError
from ingest.jobs import run_source_job
from ingest.runs import RunStats
from models.ingest_run.db import IngestRunDB
from models.source.db import SourceDB

FANDOM = SourceKind.FANDOM_PAGE


def gundam_page() -> SourceDB:
    """Build a source row for a job to add through its own session."""
    return SourceDB(
        content_license=ContentLicense.CC_BY_SA_3_0,
        external_id="2196",
        kind=FANDOM,
        retrieved_at=get_mock_utcnow(),
        url="https://gundam.fandom.com/?curid=2196",
    )


def count(test_db_session: Session, model: type[IngestRunDB | SourceDB]) -> int:
    return test_db_session.execute(select(func.count()).select_from(model)).scalar_one()


def run_statuses(test_db_session: Session) -> list[IngestRunStatus]:
    test_db_session.expire_all()
    return list(test_db_session.scalars(select(IngestRunDB.status)))


class TestRunSourceJob:
    def test_runs_the_job_and_records_its_stats(
        self, test_db_session: Session, test_connection: Connection
    ) -> None:
        def job(session: Session, stats: RunStats) -> None:
            session.add(gundam_page())
            session.commit()
            stats.pages_seen = 1
            stats.rows_written = 1

        stats = run_source_job(FANDOM, job, connection=test_connection)

        assert (stats.pages_seen, stats.rows_written) == (1, 1)
        assert count(test_db_session, SourceDB) == 1
        assert run_statuses(test_db_session) == [IngestRunStatus.SUCCEEDED]

    def test_opens_its_own_connection_by_default(
        self, committed_runs: CommittedStatuses
    ) -> None:
        """The production path: no connection given; the run commits."""

        def job(session: Session, stats: RunStats) -> None:
            stats.pages_seen = 2

        stats = run_source_job(FANDOM, job)

        assert stats.pages_seen == 2
        assert committed_runs() == [(IngestRunStatus.SUCCEEDED, None)]

    def test_rolls_back_uncommitted_writes_when_the_job_fails(
        self, test_db_session: Session, test_connection: Connection
    ) -> None:
        def job(session: Session, stats: RunStats) -> None:
            session.add(gundam_page())
            session.flush()
            raise RuntimeError

        with pytest.raises(RuntimeError):
            run_source_job(FANDOM, job, connection=test_connection)

        assert count(test_db_session, SourceDB) == 0
        assert run_statuses(test_db_session) == [IngestRunStatus.FAILED]

    def test_writes_nothing_against_an_unmigrated_schema(
        self,
        test_db_session: Session,
        test_connection: Connection,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("ingest.schema.expected_heads", lambda: ["3333aaaa3333"])
        calls: list[RunStats] = []

        with pytest.raises(SchemaNotAtHeadError):
            run_source_job(
                FANDOM,
                lambda _, stats: calls.append(stats),
                connection=test_connection,
            )

        assert calls == []
        assert count(test_db_session, IngestRunDB) == 0
