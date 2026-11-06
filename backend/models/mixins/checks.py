"""Named CHECK constraints shared by several tables (RDB-14)."""

from typing import Final

from sqlalchemy import CheckConstraint

SLUG_PATTERN: Final[str] = "^[a-z0-9]+(-[a-z0-9]+)*$"
"""Lowercase words joined by single hyphens: ``ms-06f-zaku-ii``."""


def not_empty(column: str) -> CheckConstraint:
    """Reject an empty string in a ``NOT NULL`` text column."""
    return CheckConstraint(f"char_length({column}) > 0", name=f"{column}_not_empty")


def slug_format(column: str = "slug") -> CheckConstraint:
    """Require a URL slug of lowercase words joined by hyphens."""
    return CheckConstraint(f"{column} ~ '{SLUG_PATTERN}'", name=f"{column}_format")


def not_own_parent(column: str) -> CheckConstraint:
    """Stop a self-referencing row from naming itself (RDB-7)."""
    return CheckConstraint(f"{column} <> id", name="not_own_parent")
