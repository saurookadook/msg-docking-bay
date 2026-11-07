"""Run one source job: check the schema, track the run, then load.

Every source command (``fandom``, ``wikidata``, ...) calls
``run_source_job`` with its loader, so each one gets the same guard and
the same ``ingest_runs`` row.
"""

from collections.abc import Callable

from sqlalchemy import Connection
from sqlalchemy.orm import Session

from constants.catalog import SourceKind
from db.db_session_manager import DBSessionManager
from ingest.runs import RunStats, track_run
from ingest.schema import assert_schema_at_head

type Job = Callable[[Session, RunStats], None]
"""A loader: writes through the session, commits per unit of work
(SQLA-15), and fills in the stats."""


def run_source_job(
    kind: SourceKind, job: Job, *, connection: Connection | None = None
) -> RunStats:
    """Run ``job`` for ``kind`` and return the stats it reported.

    The job's session is on the connection that holds the run's lock,
    so a run that loses its lock cannot commit anything more. The job
    commits its own work; anything it has not committed when it raises
    is rolled back when the session closes, while the run row still
    records the failure.

    Args:
        kind: The source kind the job reads.
        job: The loader.
        connection: The connection to run on. Defaults to a new one;
            tests pass their rolled-back connection.

    Raises:
        SchemaNotAtHeadError: The database is not at the backend's
            head; nothing is written, not even a run row.
        RunInProgressError: Another run of ``kind`` is in progress.
        RunLostError: The run lost its lock and was taken over.
    """
    if connection is None:
        with DBSessionManager().engine.connect() as check:
            assert_schema_at_head(check)
    else:
        assert_schema_at_head(connection)

    with track_run(kind, connection=connection) as run, run.session() as session:
        job(session, run.stats)
    return run.stats
