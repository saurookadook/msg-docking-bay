"""Write the API's OpenAPI schema to a file (MONO-13).

The schema is the API contract: the frontend generates its TypeScript
types from it. Keys are sorted so the output only changes when the API
does. Importing the app starts no server and opens no database
connection, so this runs anywhere the backend's environment is
installed.

Run it through ``pnpm run api:generate`` in ``frontend/``, or directly
with ``uv run python -m scripts.export_openapi <output>``.
"""

import argparse
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from api.app.main import app
from utils.logging.init import init_logging

DESCRIPTION: Final = "Write the API's OpenAPI schema to a file."

logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Write the schema to a path, creating its parent directories."""
    init_logging(app_name="export-openapi")
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "output", type=Path, help="the file to write, such as openapi.json"
    )
    args = parser.parse_args(argv)
    output: Path = args.output

    schema = json.dumps(app.openapi(), indent=2, sort_keys=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(schema + "\n", encoding="utf-8")

    logger.info("Wrote the OpenAPI schema to '%s'", output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
