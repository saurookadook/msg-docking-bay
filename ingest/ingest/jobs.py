"""Run one source job: check the schema, track the run, then load.

Every source command (``fandom``, ``wikidata``, ...) calls
``run_source_job`` with its loader, so each one gets the same guard and
the same ``ingest_runs`` row.
"""

from collections.abc import Callable

from sqlalchemy.orm import Session

from constants.catalog import SourceKind
from db.db_session_manager import DBSessionManager
from ingest.runs import RunStats, SessionFactory, track_run
from ingest.schema import assert_schema_at_head

type Job = Callable[[Session, RunStats], None]
"""A loader: writes through the session, commits per unit of work
(SQLA-15), and fills in the stats."""


def run_source_job(
    kind: SourceKind, job: Job, *, session_factory: SessionFactory | None = None
) -> RunStats:
    """Run ``job`` for ``kind`` and return the stats it reported.

    The job owns its session and commits its own work; anything it has
    not committed when it raises is rolled back when the session
    closes, while the run row still records the failure.

    Raises:
        SchemaNotAtHeadError: The database is not at the backend's
            head; nothing is written, not even a run row.
        RunInProgressError: Another run of ``kind`` is in progress.
    """
    sessions = session_factory or DBSessionManager().scoped_session.session_factory
    with sessions() as session:
        assert_schema_at_head(session.connection())

    with track_run(kind, session_factory=sessions) as stats, sessions() as session:
        job(session, stats)
    return stats
