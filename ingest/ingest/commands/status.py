"""``ingest status``: the schema, and each source kind's latest run."""

import argparse
from datetime import datetime

from rich.console import Console
from rich.table import Column, Table

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
    # Fold rather than truncate: a non-terminal console (a pipe, or a
    # container without a TTY) is 80 columns, and every value must
    # still show in full. Six columns keep the headers whole there.
    table = Table(
        Column("Source", no_wrap=True),
        *(
            Column(header, min_width=len(header), overflow="fold")
            for header in ("Last run", "Started", "Finished", "Counts", "Watermark")
        ),
        caption="Counts: pages seen / rows written / errors",
    )
    for kind in SourceKind:
        run = latest.get(kind)
        last_success = succeeded.get(kind)
        watermark = _when(last_success.watermark_at) if last_success else NEVER
        if run is None:
            table.add_row(kind.value, "never", NEVER, NEVER, NEVER, watermark)
            continue
        status = run.status.value
        if run.error_summary:
            status = f"{status} ({run.error_summary})"
        table.add_row(
            kind.value,
            status,
            _when(run.started_at),
            _when(run.finished_at),
            f"{run.pages_seen} / {run.rows_written} / {run.error_count}",
            watermark,
        )
    return table


def _when(moment: datetime | None) -> str:
    return moment.isoformat(timespec="seconds") if moment else NEVER
