"""Check that the database is at the backend's Alembic head.

The ingest image carries the backend's models and revisions, but the
database is migrated separately (``moon run backend:migrate``), by the
owner role. A database behind the image, or ahead of it, has a schema
the models do not describe, so every command that writes checks first.
"""

from collections.abc import Collection
from pathlib import Path
from typing import Final

from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection

import db
from ingest.errors import SchemaNotAtHeadError

MIGRATIONS_DIR: Final = Path(db.__file__).parent / "migrations"
"""The backend's Alembic folder. Found through ``db`` rather than
``alembic.ini``, which is not part of the installed package, and not
through ``db.migrations``, which is not a regular package.
"""

MIGRATE_HINT: Final = "Run `moon run backend:migrate`, then try again."

UPDATE_HINT: Final = (
    "The database was migrated by a newer backend; update this checkout and"
    " rebuild the ingest image."
)


def expected_heads() -> list[str]:
    """Return the head revisions the backend's migrations define."""
    return _script_directory().get_heads()


def known_revisions() -> set[str]:
    """Return every revision the backend's migrations define."""
    return {script.revision for script in _script_directory().walk_revisions()}


def current_heads(connection: Connection) -> tuple[str, ...]:
    """Return the revisions in the database's ``alembic_version``."""
    return MigrationContext.configure(connection).get_current_heads()


def assert_schema_at_head(connection: Connection) -> tuple[str, ...]:
    """Return the database's heads, or raise unless they are the head.

    Raises:
        SchemaNotAtHeadError: The database is behind, ahead, or
            unmigrated.
    """
    current = current_heads(connection)
    check_heads(expected=expected_heads(), current=current, known=known_revisions())
    return current


def check_heads(
    *, expected: Collection[str], current: Collection[str], known: Collection[str]
) -> None:
    """Compare the database's heads with the backend's; pure.

    ``known`` tells a database that is behind (migrate it) from one
    migrated by a newer backend than this build (update the build).

    Raises:
        SchemaNotAtHeadError: The heads differ.
    """
    if set(current) == set(expected):
        return
    wanted = _join(expected)
    if not current:
        raise SchemaNotAtHeadError(
            f"The database has no migrations applied; the backend's head is"
            f" '{wanted}'. {MIGRATE_HINT}"
        )
    hint = UPDATE_HINT if set(current) - set(known) else MIGRATE_HINT
    raise SchemaNotAtHeadError(
        f"The database is at revision '{_join(current)}', not the backend's"
        f" head '{wanted}'. {hint}"
    )


def _script_directory() -> ScriptDirectory:
    return ScriptDirectory(MIGRATIONS_DIR)


def _join(revisions: Collection[str]) -> str:
    return ", ".join(sorted(revisions))
