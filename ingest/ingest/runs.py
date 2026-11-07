"""Record each ingest run in ``ingest_runs``.

``track_run`` wraps one load or sync of one source kind. It holds an
advisory lock so two runs of a kind never overlap, and every write of
the run goes through the connection that holds the lock: the run row
and the job's data alike. The lock lives as long as that connection's
database session, and a guard refuses every statement once SQLAlchemy
has replaced it, so a run that lost its lock can write nothing more.

The run row is written in short transactions of its own, before and
after the job's: a job whose transaction rolls back still leaves its
``failed`` row behind.
"""

import logging
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Final
from uuid import UUID

import psycopg
from sqlalchemy import Connection, TextClause, event, func, select, text, update
from sqlalchemy.dialects.postgresql import distinct_on
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from constants.catalog import IngestRunStatus, SourceKind
from db.db_session_manager import DBSessionManager
from ingest.errors import RunInProgressError, RunLostError
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


@dataclass(frozen=True)
class Run:
    """A run in progress: its row, its stats, and its connection."""

    connection: Connection
    """Holds the run's lock. Every write of the run goes through it."""
    id: UUID
    stats: RunStats

    def session(self) -> Session:
        """Open a session on the run's connection, for the job's writes.

        Close it before the ``track_run`` block ends: the run row is
        written on the same connection, after the job's transaction.
        """
        return _session_on(self.connection)


@contextmanager
def track_run(
    kind: SourceKind, *, connection: Connection | None = None
) -> Generator[Run]:
    """Record a run of ``kind`` from start to finish.

    The run row is ``running`` while the block runs, then ``succeeded``
    or, if the block raises, ``failed`` with the error summarized by
    ``summarize_error``; the exception is re-raised.

    Args:
        kind: The source kind the job reads.
        connection: The connection to lock and write through. Defaults
            to a new one from the engine, closed when the run ends;
            tests pass their rolled-back connection.

    Yields:
        The run, whose ``session()`` the job writes through and whose
        ``stats`` it fills in.

    Raises:
        RunInProgressError: Another run of ``kind`` holds the lock.
        RunLostError: Another run marked this one abandoned before it
            finished, so its outcome was not recorded.
    """
    with _own_or_given(connection) as conn, _run_lock(conn, kind):
        run = Run(connection=conn, id=_start_run(conn, kind), stats=RunStats())
        try:
            yield run
        # BaseException: a Ctrl-C also ends the run, and is re-raised.
        except BaseException as exc:
            _finish_run(
                run,
                status=IngestRunStatus.FAILED,
                error_summary=summarize_error(exc),
            )
            raise
        _finish_run(run, status=IngestRunStatus.SUCCEEDED, error_summary=None)


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


@dataclass(frozen=True)
class RunSummary:
    """One run, as the ``status`` command reports it."""

    error_count: int
    error_summary: str | None
    finished_at: datetime | None
    pages_seen: int
    rows_written: int
    started_at: datetime
    status: IngestRunStatus
    watermark_at: datetime | None


def latest_runs(
    session: Session, *, status: IngestRunStatus | None = None
) -> dict[SourceKind, RunSummary]:
    """Return each source kind's newest run, optionally of one status.

    One ``DISTINCT ON`` query rather than one per kind; a kind with no
    such run is missing from the result.
    """
    stmt = select(IngestRunDB).ext(distinct_on(IngestRunDB.source_kind))
    if status is not None:
        stmt = stmt.where(IngestRunDB.status == status)
    stmt = stmt.order_by(
        IngestRunDB.source_kind,
        IngestRunDB.started_at.desc(),
        IngestRunDB.id.desc(),
    )
    return {
        run.source_kind: RunSummary(
            error_count=run.error_count,
            error_summary=run.error_summary,
            finished_at=run.finished_at,
            pages_seen=run.pages_seen,
            rows_written=run.rows_written,
            started_at=run.started_at,
            status=run.status,
            watermark_at=run.watermark_at,
        )
        for run in session.scalars(stmt)
    }


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


def _session_on(connection: Connection) -> Session:
    # The process's session settings (SQLA-14), bound to one connection.
    # create_savepoint: on a connection already in a transaction (a
    # test's), commits become savepoints; otherwise they commit.
    return DBSessionManager().scoped_session.session_factory(
        bind=connection, join_transaction_mode="create_savepoint"
    )


@contextmanager
def _own_or_given(connection: Connection | None) -> Generator[Connection]:
    if connection is not None:
        yield connection
        return
    with DBSessionManager().engine.connect() as own:
        yield own


@contextmanager
def _run_lock(connection: Connection, kind: SourceKind) -> Generator[None]:
    """Hold the session-level advisory lock for ``kind``.

    Session-level, with the connection left idle outside a transaction
    between the run's writes, because a transaction-level lock would
    need a transaction open for the whole run, which
    ``idle_in_transaction_session_timeout`` ends after 30 seconds. The
    server releases it if the connection or the process dies.

    NOTE: after a disconnect, SQLAlchemy reconnects a ``Connection`` on
    its next use, to a new database session that does not hold the
    lock. The guard refuses every statement on any DBAPI connection but
    the one that took the lock.

    Raises:
        RunInProgressError: Another connection holds the lock.
    """
    params = {"namespace": LOCK_NAMESPACE, "kind": kind.value}
    acquired = _execute_and_end(
        connection,
        text("SELECT pg_try_advisory_lock(:namespace, hashtext(:kind))"),
        params,
    )
    if not acquired:
        raise RunInProgressError(
            f"Another '{kind.value}' run is in progress; wait for it to finish."
        )
    locked = connection.connection.dbapi_connection

    def guard(
        conn: Connection,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        if conn.connection.dbapi_connection is not locked:
            raise RunLostError(
                f"The '{kind.value}' run lost its database connection, and its"
                " lock with it; it cannot write any more."
            )

    event.listen(connection, "before_cursor_execute", guard)
    try:
        yield
    finally:
        _release_lock(connection, params)
        event.remove(connection, "before_cursor_execute", guard)


def _release_lock(connection: Connection, params: Mapping[str, object]) -> None:
    try:
        _execute_and_end(
            connection,
            text("SELECT pg_advisory_unlock(:namespace, hashtext(:kind))"),
            params,
        )
    except DBAPIError, RunLostError:
        # NOTE: a pooled connection must not keep the lock; dropping it
        # makes the server release the lock instead.
        logger.warning("Could not release the run lock; dropping its connection")
        connection.invalidate()


def _execute_and_end(
    connection: Connection, statement: TextClause, params: Mapping[str, object]
) -> object:
    """Run one statement, committing only a transaction it began.

    The lock's connection must be idle between the run's writes; a
    connection already in a transaction (a test's) is left in it.
    """
    began = not connection.in_transaction()
    result = connection.execute(statement, params).scalar_one()
    if began:
        connection.commit()
    return result


def _start_run(connection: Connection, kind: SourceKind) -> UUID:
    with _session_on(connection) as session, session.begin():
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
    run: Run, *, status: IngestRunStatus, error_summary: str | None
) -> None:
    """Record the run's outcome, unless it is no longer ``running``.

    Fenced on ``status = 'running'``: a later run that marked this one
    abandoned has the final word, and this run's outcome is dropped.
    """
    stats = run.stats
    with _session_on(run.connection) as session, session.begin():
        updated = session.scalars(
            update(IngestRunDB)
            .where(
                IngestRunDB.id == run.id,
                IngestRunDB.status == IngestRunStatus.RUNNING,
            )
            .values(
                error_count=stats.error_count,
                error_summary=error_summary,
                finished_at=func.now(),
                pages_seen=stats.pages_seen,
                rows_written=stats.rows_written,
                status=status,
                watermark_at=stats.watermark_at,
            )
            .returning(IngestRunDB.id)
        ).all()
    if not updated:
        raise RunLostError(
            f"Run id='{run.id}' was marked abandoned by a later run before it"
            f" finished; its outcome ({status.value}) was not recorded."
        )
    logger.info(
        "Finished run id='%s' as %s: pages_seen=%s rows_written=%s errors=%s",
        run.id,
        status.value,
        stats.pages_seen,
        stats.rows_written,
        stats.error_count,
    )
