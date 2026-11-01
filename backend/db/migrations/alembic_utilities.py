"""Helpers that wrap ``op`` calls for migrations (ALEM-9, ALEM-11).

Migrations import these, never application code, so the helpers take
literal values and build their own types.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def create_pg_enum(name: str, values: Sequence[str]) -> sa.Enum:
    """Create a PostgreSQL enum type and return it for column use.

    The returned type has ``create_type=False``, so a ``create_table``
    that uses it does not try to create the type a second time.
    """
    enum_type: sa.Enum = postgresql.ENUM(*values, name=name, create_type=False)
    enum_type.create(op.get_bind(), checkfirst=False)
    return enum_type


def drop_pg_enum(name: str, values: Sequence[str]) -> None:
    """Drop a PostgreSQL enum type, after the tables that use it."""
    enum_type: sa.Enum = postgresql.ENUM(*values, name=name, create_type=False)
    enum_type.drop(op.get_bind(), checkfirst=False)
