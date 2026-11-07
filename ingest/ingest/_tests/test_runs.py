from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.ingest_run.db import IngestRunDBFactory
from constants.catalog import IngestRunStatus, SourceKind
from ingest.errors import RunInProgressError
from ingest.runs import (
    ABANDONED,
    LOCK_NAMESPACE,
    SessionFactory,
    latest_runs,
    latest_watermark,
    summarize_error,
    track_run,
)
from models.ingest_run.db import IngestRunDB

FANDOM = SourceKind.FANDOM_PAGE
WIKIDATA = SourceKind.WIKIDATA_ITEM
WATERMARK = datetime(2025, 9, 1, 12, 0, tzinfo=UTC)


def runs(test_db_session: Session) -> list[IngestRunDB]:
    test_db_session.expire_all()  # rows written through other sessions
    return list(
        test_db_session.scalars(
            select(IngestRunDB).order_by(IngestRunDB.source_kind, IngestRunDB.id)
        )
    )


def held_run_locks(test_db_session: Session) -> int:
    return test_db_session.execute(
        text(
            "SELECT count(*) FROM pg_locks"
            " WHERE locktype = 'advisory' AND classid = :namespace"
        ),
        {"namespace": LOCK_NAMESPACE},
    ).scalar_one()


class TestTrackRun:
    def test_records_a_succeeded_run_with_its_stats(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        with track_run(FANDOM, session_factory=run_sessions) as stats:
            stats.pages_seen = 3
            stats.rows_written = 2
            stats.error_count = 1
            stats.watermark_at = WATERMARK

        [run] = runs(test_db_session)
        assert run.source_kind is FANDOM
        assert run.status is IngestRunStatus.SUCCEEDED
        assert (run.pages_seen, run.rows_written, run.error_count) == (3, 2, 1)
        assert run.watermark_at == WATERMARK
        assert run.error_summary is None
        assert run.finished_at is not None
        assert run.finished_at >= run.started_at

    def test_keeps_the_run_running_while_the_job_works(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        with track_run(FANDOM, session_factory=run_sessions):
            [run] = runs(test_db_session)

            assert run.status is IngestRunStatus.RUNNING
            assert run.finished_at is None

    def test_records_a_failed_run_without_the_error_message(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        with (
            pytest.raises(ValueError, match="Char Aznable"),
            track_run(FANDOM, session_factory=run_sessions) as stats,
        ):
            stats.pages_seen = 7
            raise ValueError("bad infobox on Char Aznable's page")

        [run] = runs(test_db_session)
        assert run.status is IngestRunStatus.FAILED
        assert run.error_summary == "ValueError"
        assert run.pages_seen == 7
        assert run.finished_at is not None

    def test_keeps_the_failed_run_when_the_jobs_writes_roll_back(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        """The run row is written apart from the job's transaction."""
        with (
            pytest.raises(IntegrityError),
            track_run(FANDOM, session_factory=run_sessions),
            run_sessions() as job_session,
            job_session.begin(),
        ):
            job_session.add(IngestRunDB(source_kind=WIKIDATA, pages_seen=-1))

        [run] = runs(test_db_session)
        assert run.source_kind is FANDOM
        assert run.status is IngestRunStatus.FAILED
        assert run.error_summary == "23514 ck_ingest_runs_pages_seen_not_negative"

    def test_marks_a_leftover_running_run_of_its_kind_abandoned(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        """Holding the lock proves no live process owns that row."""
        leftover = IngestRunDBFactory(source_kind=FANDOM)
        other_kind = IngestRunDBFactory(source_kind=WIKIDATA)
        test_db_session.commit()

        with track_run(FANDOM, session_factory=run_sessions):
            pass

        by_id = {run.id: run for run in runs(test_db_session)}
        assert by_id[leftover.id].status is IngestRunStatus.FAILED
        assert by_id[leftover.id].error_summary == ABANDONED
        assert by_id[leftover.id].finished_at is not None
        assert by_id[other_kind.id].status is IngestRunStatus.RUNNING
        assert len(by_id) == 3


class TestRunLock:
    def test_rejects_a_second_run_of_the_same_kind(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        with track_run(FANDOM, session_factory=run_sessions):
            with (
                pytest.raises(RunInProgressError, match="'fandom_page' run"),
                track_run(FANDOM, session_factory=run_sessions),
            ):
                pass

            assert len(runs(test_db_session)) == 1

    def test_allows_a_run_of_another_kind_meanwhile(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        with (
            track_run(FANDOM, session_factory=run_sessions),
            track_run(WIKIDATA, session_factory=run_sessions),
        ):
            assert held_run_locks(test_db_session) == 2

    def test_releases_the_lock_after_a_failed_run(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        with (
            pytest.raises(RuntimeError),
            track_run(FANDOM, session_factory=run_sessions),
        ):
            raise RuntimeError

        assert held_run_locks(test_db_session) == 0
        with track_run(FANDOM, session_factory=run_sessions):
            pass

    def test_drops_the_lock_connection_when_unlocking_fails(
        self, test_db_session: Session, run_sessions: SessionFactory
    ) -> None:
        """A pooled connection must never keep a run lock."""
        with track_run(FANDOM, session_factory=run_sessions):
            test_db_session.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_locks"
                    " WHERE locktype = 'advisory' AND classid = :namespace"
                ),
                {"namespace": LOCK_NAMESPACE},
            )

        [run] = runs(test_db_session)
        assert run.status is IngestRunStatus.SUCCEEDED
        assert held_run_locks(test_db_session) == 0
        with track_run(FANDOM, session_factory=run_sessions):
            pass


class TestLatestWatermark:
    def test_returns_the_newest_succeeded_runs_watermark(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        def run(hours: int, status: IngestRunStatus, kind: SourceKind = FANDOM) -> None:
            started_at = mock_utcnow + timedelta(hours=hours)
            IngestRunDBFactory(
                finished_at=None if status is IngestRunStatus.RUNNING else started_at,
                source_kind=kind,
                started_at=started_at,
                status=status,
                watermark_at=WATERMARK + timedelta(days=hours),
            )

        run(1, IngestRunStatus.SUCCEEDED)
        run(2, IngestRunStatus.SUCCEEDED)
        run(3, IngestRunStatus.FAILED)
        run(4, IngestRunStatus.RUNNING)
        run(5, IngestRunStatus.SUCCEEDED, kind=WIKIDATA)
        test_db_session.commit()

        assert latest_watermark(test_db_session, FANDOM) == WATERMARK + timedelta(
            days=2
        )

    def test_returns_none_before_any_run_succeeds(
        self, test_db_session: Session
    ) -> None:
        IngestRunDBFactory(source_kind=FANDOM)
        test_db_session.commit()

        assert latest_watermark(test_db_session, FANDOM) is None


class TestLatestRuns:
    def test_returns_each_kinds_newest_run(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        older, newer = mock_utcnow, mock_utcnow + timedelta(hours=1)
        IngestRunDBFactory(
            finished_at=older,
            source_kind=FANDOM,
            started_at=older,
            status=IngestRunStatus.SUCCEEDED,
            watermark_at=WATERMARK,
        )
        IngestRunDBFactory(
            error_summary="ValueError",
            finished_at=newer,
            pages_seen=4,
            source_kind=FANDOM,
            started_at=newer,
            status=IngestRunStatus.FAILED,
        )
        IngestRunDBFactory(source_kind=WIKIDATA, started_at=older)
        test_db_session.commit()

        latest = latest_runs(test_db_session)

        assert set(latest) == {FANDOM, WIKIDATA}
        assert latest[FANDOM].status is IngestRunStatus.FAILED
        assert latest[FANDOM].error_summary == "ValueError"
        assert latest[FANDOM].pages_seen == 4
        assert latest[WIKIDATA].status is IngestRunStatus.RUNNING

        succeeded = latest_runs(test_db_session, status=IngestRunStatus.SUCCEEDED)

        assert set(succeeded) == {FANDOM}
        assert succeeded[FANDOM].watermark_at == WATERMARK


class TestSummarizeError:
    def test_names_the_sqlstate_and_constraint(self, test_db_session: Session) -> None:
        test_db_session.add(IngestRunDB(source_kind=FANDOM, error_count=-1))

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert summarize_error(exc_info.value) == (
            "23514 ck_ingest_runs_error_count_not_negative"
        )

    def test_names_only_the_sqlstate_without_a_constraint(
        self, test_db_session: Session
    ) -> None:
        with pytest.raises(Exception) as exc_info, test_db_session.begin_nested():
            test_db_session.execute(text("SELECT 1 / 0"))

        assert summarize_error(exc_info.value) == "22012"

    def test_names_the_class_of_any_other_error(self) -> None:
        assert summarize_error(KeyError("RX-78-2")) == "KeyError"
