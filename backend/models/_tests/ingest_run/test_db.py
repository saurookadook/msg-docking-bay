import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.ingest_run.db import IngestRunDBFactory
from _mocks.temporal import MOCK_UTCNOW
from constants.catalog import IngestRunStatus, SourceKind
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.ingest_run.db import IngestRunDB

RUN_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba001")
FINISHED_AT = MOCK_UTCNOW + timedelta(minutes=3)


class TestIngestRunDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        watermark_at = datetime(2025, 8, 25, 23, 41, tzinfo=UTC)
        IngestRunDBFactory(
            id=RUN_ID,
            error_count=2,
            error_summary="23514 ck_spec_sheets_head_height_m_positive x2",
            finished_at=FINISHED_AT,
            pages_seen=3976,
            rows_written=11928,
            source_kind=SourceKind.FANDOM_PAGE,
            started_at=mock_utcnow,
            status=IngestRunStatus.SUCCEEDED,
            watermark_at=watermark_at,
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        run = test_db_session.execute(
            select(IngestRunDB).where(IngestRunDB.id == RUN_ID)
        ).scalar_one()

        assert run.error_count == 2
        assert run.error_summary == "23514 ck_spec_sheets_head_height_m_positive x2"
        assert run.finished_at == FINISHED_AT
        assert run.pages_seen == 3976
        assert run.rows_written == 11928
        assert run.source_kind is SourceKind.FANDOM_PAGE
        assert run.started_at == mock_utcnow
        assert run.status is IngestRunStatus.SUCCEEDED
        assert run.watermark_at == watermark_at
        assert run.created_at == mock_utcnow

    def test_defaults_a_new_run_to_running_with_zero_counts(
        self, test_db_session: Session
    ) -> None:
        """The loader opens a run with one bare INSERT."""
        test_db_session.execute(
            text(
                "INSERT INTO ingest_runs (id, source_kind) VALUES (:id, 'fandom_page')"
            ),
            {"id": RUN_ID},
        )

        row = test_db_session.execute(
            text(
                "SELECT status::text, error_count, pages_seen, rows_written,"
                " started_at IS NOT NULL, finished_at FROM ingest_runs WHERE id = :id"
            ),
            {"id": RUN_ID},
        ).one()

        assert tuple(row) == ("running", 0, 0, 0, True, None)

    def test_shares_the_source_kind_type_with_sources(self) -> None:
        """One type, so the two columns can never drift apart (PG-5)."""
        runs: Table = BaseDB.metadata.tables["ingest_runs"]
        sources: Table = BaseDB.metadata.tables["sources"]

        assert runs.c.source_kind.type is sources.c.kind.type

    def test_indexes_the_watermark_lookup(self) -> None:
        runs: Table = BaseDB.metadata.tables["ingest_runs"]

        assert {
            index.name: [c.name for c in index.columns] for index in runs.indexes
        } == {
            "ix_ingest_runs_source_kind_status_started_at": [
                "source_kind",
                "status",
                "started_at",
            ],
        }


class TestIngestRunDBConstraints:
    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"error_count": -1}, "ck_ingest_runs_error_count_not_negative"),
            ({"error_summary": ""}, "ck_ingest_runs_error_summary_not_empty"),
            ({"pages_seen": -1}, "ck_ingest_runs_pages_seen_not_negative"),
            ({"rows_written": -1}, "ck_ingest_runs_rows_written_not_negative"),
            (
                {
                    "finished_at": MOCK_UTCNOW - timedelta(seconds=1),
                    "status": IngestRunStatus.FAILED,
                },
                "ck_ingest_runs_finished_after_started",
            ),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        IngestRunDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    @pytest.mark.parametrize(
        "status, finished_at",
        [
            (IngestRunStatus.RUNNING, FINISHED_AT),
            (IngestRunStatus.SUCCEEDED, None),
            (IngestRunStatus.FAILED, None),
        ],
    )
    def test_rejects_a_finish_time_that_disagrees_with_the_status(
        self,
        test_db_session: Session,
        status: IngestRunStatus,
        finished_at: datetime | None,
    ) -> None:
        IngestRunDBFactory(status=status, finished_at=finished_at)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_ingest_runs_finished_unless_running",
        )

    @pytest.mark.parametrize(
        "status", [IngestRunStatus.SUCCEEDED, IngestRunStatus.FAILED]
    )
    def test_accepts_a_finished_run(
        self, test_db_session: Session, status: IngestRunStatus
    ) -> None:
        IngestRunDBFactory(status=status, finished_at=FINISHED_AT)

        test_db_session.flush()
