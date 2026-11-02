"""The ``ingest_runs`` table: each load or sync, and its watermark."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import IngestRunStatus, SourceKind
from constants.db_types import INGEST_RUN_STATUS_DB_TYPE, SOURCE_KIND_DB_TYPE
from db.base_db import BaseDB
from models.mixins.checks import not_empty
from models.mixins.db import TimestampsDB


class IngestRunDB(BaseDB, TimestampsDB):
    """One run of the ingest service against one kind of source.

    The current watermark is not stored: it is the ``watermark_at`` of
    the latest succeeded run for the source kind (RDB-1), which the
    ``(source_kind, status, started_at)`` index serves.
    """

    error_count: Mapped[int] = mapped_column(server_default="0")
    error_summary: Mapped[str | None]
    """SQLSTATEs and constraint names only, never row data or prose."""
    finished_at: Mapped[datetime | None]
    """Null exactly while the run is ``running``."""
    pages_seen: Mapped[int] = mapped_column(server_default="0")
    rows_written: Mapped[int] = mapped_column(server_default="0")
    source_kind: Mapped[SourceKind] = mapped_column(SOURCE_KIND_DB_TYPE)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    status: Mapped[IngestRunStatus] = mapped_column(
        INGEST_RUN_STATUS_DB_TYPE, server_default=IngestRunStatus.RUNNING.value
    )
    watermark_at: Mapped[datetime | None]
    """The newest upstream revision time this run saw.

    The next delta sync reads upstream changes after it.
    """

    __table_args__ = (
        CheckConstraint("error_count >= 0", name="error_count_not_negative"),
        not_empty("error_summary"),
        CheckConstraint("finished_at >= started_at", name="finished_after_started"),
        CheckConstraint(
            "(status = 'running') = (finished_at IS NULL)",
            name="finished_unless_running",
        ),
        CheckConstraint("pages_seen >= 0", name="pages_seen_not_negative"),
        CheckConstraint("rows_written >= 0", name="rows_written_not_negative"),
        Index(
            "ix_ingest_runs_source_kind_status_started_at",
            "source_kind",
            "status",
            "started_at",
        ),
    )
