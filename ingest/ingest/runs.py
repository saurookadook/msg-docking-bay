"""Record each ingest run in ``ingest_runs``.

``track_run`` wraps one load or sync of one source kind. It holds an
advisory lock so two runs of a kind never overlap, and writes the run
row in short transactions of its own, separate from the job's data
writes: a job whose transaction rolls back still leaves its ``failed``
row behind.
"""

import logging
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Final
from uuid import UUID

import psycopg
from sqlalchemy import Connection, func, select, text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from constants.catalog import IngestRunStatus, SourceKind
from db.db_session_manager import DBSessionManager
from ingest.errors import RunInProgressError
from models.ingest_run.db import IngestRunDB

logger = logging.getLogger(__name__)

LOCK_NAMESPACE: Final = 0x1D6E57
"""The first key of each run lock, so ingest's advisory locks cannot
collide with another feature's; the second is ``hashtext(kind)``.
"""

ABANDONED: Final = "abandoned"
"""The ``error_summary`` of a run found still ``running`` by the next
run of its kind, which can only mean its process died.
"""

type SessionFactory = Callable[[], Session]


@dataclass
class RunStats:
    """What a job reports back about its run; the job updates it.

    A run that sees nothing newer than the last watermark sets
    ``watermark_at`` to that watermark, so the next run starts from the
    same point. It is the newest *upstream* revision time seen, never
    the local clock.
    """

    error_count: int = 0
    pages_seen: int = 0
    rows_written: int = 0
    watermark_at: datetime | None = None


@contextmanager
def track_run(
    kind: SourceKind, *, session_factory: SessionFactory | None = None
) -> Generator[RunStats]:
    """Record a run of ``kind`` from start to finish.

    The run row is ``running`` while the block runs, then ``succeeded``
    or, if the block raises, ``failed`` with the error summarized by
    ``summarize_error``; the exception is re-raised.

    Args:
        kind: The source kind the job reads.
        session_factory: Opens the sessions that write the run row.
            Defaults to the process's session factory; tests pass one
            bound to their rolled-back connection.

    Yields:
        The stats the job fills in.

    Raises:
        RunInProgressError: Another run of ``kind`` holds the lock.
    """
    sessions = session_factory or DBSessionManager().scoped_session.session_factory
    with _run_lock(kind):
        run_id = _start_run(kind, sessions=sessions)
        stats = RunStats()
        try:
            yield stats
        # BaseException: a Ctrl-C also ends the run, and is re-raised.
        except BaseException as exc:
            _finish_run(
                run_id,
                status=IngestRunStatus.FAILED,
                stats=stats,
                error_summary=summarize_error(exc),
                sessions=sessions,
            )
            raise
        _finish_run(
            run_id,
            status=IngestRunStatus.SUCCEEDED,
            stats=stats,
            error_summary=None,
            sessions=sessions,
        )


def latest_watermark(session: Session, kind: SourceKind) -> datetime | None:
    """Return the watermark of the latest succeeded run of ``kind``.

    ``None`` when no run has succeeded, or the latest set none: either
    way the next sync starts from a full baseline. The
    ``(source_kind, status, started_at)`` index serves the query.
    """
    return session.execute(
        select(IngestRunDB.watermark_at)
        .where(
            IngestRunDB.source_kind == kind,
            IngestRunDB.status == IngestRunStatus.SUCCEEDED,
        )
        .order_by(IngestRunDB.started_at.desc(), IngestRunDB.id.desc())
        .limit(1)
    ).scalar_one_or_none()


def summarize_error(exc: BaseException) -> str:
    """Return the SQLSTATE and constraint, or the exception class name.

    Never the message: it can quote row values or upstream text, which
    ``error_summary`` must not hold.
    """
    orig = exc.orig if isinstance(exc, DBAPIError) else exc
    if isinstance(orig, psycopg.Error) and orig.sqlstate:
        constraint = orig.diag.constraint_name
        return f"{orig.sqlstate} {constraint}" if constraint else orig.sqlstate
    return type(exc).__name__


@contextmanager
def _run_lock(kind: SourceKind) -> Generator[None]:
    """Hold the session-level advisory lock for ``kind``.

    Session-level, on a connection of its own that stays idle outside a
    transaction, because a transaction-level lock would need a
    transaction open for the whole run, which
    ``idle_in_transaction_session_timeout`` ends after 30 seconds. The
    server releases it if the process dies.
    """
    params = {"namespace": LOCK_NAMESPACE, "kind": kind.value}
    with DBSessionManager().engine.connect() as connection:
        acquired = connection.execute(
            text("SELECT pg_try_advisory_lock(:namespace, hashtext(:kind))"), params
        ).scalar_one()
        connection.commit()
        if not acquired:
            raise RunInProgressError(
                f"Another '{kind.value}' run is in progress; wait for it to finish."
            )
        try:
            yield
        finally:
            _release_lock(connection, params)


def _release_lock(connection: Connection, params: Mapping[str, object]) -> None:
    try:
        connection.execute(
            text("SELECT pg_advisory_unlock(:namespace, hashtext(:kind))"), params
        )
        connection.commit()
    except DBAPIError:
        # NOTE: a pooled connection must not keep the lock; dropping it
        # makes the server release the lock instead.
        logger.warning("Could not release the run lock; dropping its connection")
        connection.invalidate()


def _start_run(kind: SourceKind, *, sessions: SessionFactory) -> UUID:
    with sessions() as session, session.begin():
        abandoned = session.scalars(
            update(IngestRunDB)
            .where(
                IngestRunDB.source_kind == kind,
                IngestRunDB.status == IngestRunStatus.RUNNING,
            )
            .values(
                error_summary=ABANDONED,
                finished_at=func.now(),
                status=IngestRunStatus.FAILED,
            )
            .returning(IngestRunDB.id)
        ).all()
        if abandoned:
            logger.warning(
                "Marked %s abandoned '%s' run(s) as failed", len(abandoned), kind.value
            )
        run = IngestRunDB(source_kind=kind)
        session.add(run)
        session.flush()
        logger.info("Started '%s' run id='%s'", kind.value, run.id)
        return run.id


def _finish_run(
    run_id: UUID,
    *,
    status: IngestRunStatus,
    stats: RunStats,
    error_summary: str | None,
    sessions: SessionFactory,
) -> None:
    with sessions() as session, session.begin():
        run = session.get_one(IngestRunDB, run_id)
        run.error_count = stats.error_count
        run.error_summary = error_summary
        run.finished_at = session.execute(select(func.now())).scalar_one()
        run.pages_seen = stats.pages_seen
        run.rows_written = stats.rows_written
        run.status = status
        run.watermark_at = stats.watermark_at
    logger.info(
        "Finished run id='%s' as %s: pages_seen=%s rows_written=%s errors=%s",
        run_id,
        status.value,
        stats.pages_seen,
        stats.rows_written,
        stats.error_count,
    )
