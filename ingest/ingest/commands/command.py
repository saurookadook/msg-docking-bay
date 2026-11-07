"""The shape every CLI command has."""

import argparse
from collections.abc import Callable
from dataclasses import dataclass

from ingest.runs import SessionFactory


def no_arguments(parser: argparse.ArgumentParser) -> None:
    """Add nothing, for a command that takes no arguments."""


@dataclass(frozen=True)
class Command:
    """One subcommand of ``python -m ingest``.

    ``run`` returns the exit status (PY-36). It raises an
    ``IngestError`` for a failure the CLI reports with its message
    alone.
    """

    help: str
    run: Callable[[argparse.Namespace, SessionFactory], int]
    add_arguments: Callable[[argparse.ArgumentParser], None] = no_arguments
