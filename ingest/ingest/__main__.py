"""Run the ingest CLI: ``python -m ingest <command>``."""

import sys

from ingest.cli import main

if __name__ == "__main__":
    sys.exit(main())
