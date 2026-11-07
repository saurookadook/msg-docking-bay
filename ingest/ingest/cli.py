"""Load upstream catalog data into the Docking Bay database."""

import argparse
import logging
from collections.abc import Sequence

from db.db_session_manager import DBSessionManager
from ingest.commands import COMMANDS
from ingest.errors import IngestError
from ingest.runs import SessionFactory
from utils.logging.init import init_logging

APP_NAME = "ingest"


def main(
    argv: Sequence[str] | None = None, *, session_factory: SessionFactory | None = None
) -> int:
    """Run one command and return its exit status (PY-36).

    ``0`` on success, ``1`` for an ``IngestError`` (logged with its
    message alone), and ``2`` for a usage error, which ``argparse``
    exits with itself. Any other exception is unexpected and keeps its
    traceback.

    Args:
        argv: The arguments, without the program name; ``sys.argv``
            when omitted.
        session_factory: Opens the command's sessions. Defaults to the
            process's session factory; tests pass one bound to their
            rolled-back connection.
    """
    logger = init_logging(app_name=APP_NAME)
    # Alembic logs its dialect at INFO each time the schema is checked.
    logging.getLogger("alembic.runtime.migration").setLevel(logging.WARNING)
    args = build_parser().parse_args(argv)
    sessions = session_factory or DBSessionManager().scoped_session.session_factory
    try:
        return COMMANDS[args.command].run(args, sessions)
    except IngestError as exc:
        # Expected: the message says what to do, so no traceback.
        logger.error("%s", exc)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the parser, with one subcommand per registered command."""
    parser = argparse.ArgumentParser(prog="python -m ingest", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")
    for name, command in COMMANDS.items():
        subparser = subparsers.add_parser(
            name, help=command.help, description=command.help
        )
        command.add_arguments(subparser)
    return parser
