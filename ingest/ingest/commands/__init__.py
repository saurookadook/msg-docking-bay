"""The CLI's commands, registered by name (PY-35).

A new command is one module defining a ``Command`` and one entry here.
"""

from collections.abc import Mapping
from typing import Final

from ingest.commands import status
from ingest.commands.command import Command

COMMANDS: Final[Mapping[str, Command]] = {
    "status": status.COMMAND,
}

__all__ = ["COMMANDS", "Command"]
