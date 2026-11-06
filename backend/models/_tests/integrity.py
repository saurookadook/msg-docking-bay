"""Read which constraint an ``IntegrityError`` came from (RDB-29)."""

import psycopg
from sqlalchemy.exc import IntegrityError


def violated_constraint(exc: IntegrityError) -> tuple[str | None, str | None]:
    """Return the PostgreSQL ``sqlstate`` and constraint name."""
    orig = exc.orig
    assert isinstance(orig, psycopg.Error)
    return orig.sqlstate, orig.diag.constraint_name
