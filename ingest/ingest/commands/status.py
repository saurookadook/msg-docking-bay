"""``ingest status``: the schema, and each source kind's latest run."""

import argparse
from datetime import datetime

from rich.console import Console
from rich.table import Table

from constants.catalog import IngestRunStatus, SourceKind
from ingest.commands.command import Command
from ingest.runs import RunSummary, SessionFactory, latest_runs
from ingest.schema import assert_schema_at_head

NEVER = "—"


def run_status(args: argparse.Namespace, sessions: SessionFactory) -> int:
    """Print the schema revision and a table of the latest runs.

    Raises:
        SchemaNotAtHeadError: The database is not at the backend's head.
    """
    with sessions() as session:
        revision = ", ".join(assert_schema_at_head(session.connection()))
        latest = latest_runs(session)
        succeeded = latest_runs(session, status=IngestRunStatus.SUCCEEDED)

    console = Console()
    console.print(f"Schema at head: {revision}")
    console.print(_runs_table(latest, succeeded))
    return 0


COMMAND = Command(
    help="Show the schema revision and each source's latest run.", run=run_status
)


def _runs_table(
    latest: dict[SourceKind, RunSummary], succeeded: dict[SourceKind, RunSummary]
) -> Table:
    table = Table(
        "Source",
        "Last run",
        "Started",
        "Finished",
        "Pages",
        "Rows",
        "Errors",
        "Watermark",
    )
    for kind in SourceKind:
        run = latest.get(kind)
        last_success = succeeded.get(kind)
        watermark = _when(last_success.watermark_at) if last_success else NEVER
        if run is None:
            table.add_row(kind.value, "never", *[NEVER] * 5, watermark)
            continue
        status = run.status.value
        if run.error_summary:
            status = f"{status} ({run.error_summary})"
        table.add_row(
            kind.value,
            status,
            _when(run.started_at),
            _when(run.finished_at),
            str(run.pages_seen),
            str(run.rows_written),
            str(run.error_count),
            watermark,
        )
    return table


def _when(moment: datetime | None) -> str:
    return moment.isoformat(timespec="seconds") if moment else NEVER
