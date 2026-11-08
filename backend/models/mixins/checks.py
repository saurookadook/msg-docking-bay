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


def positive(column: str) -> CheckConstraint:
    """Require a number above zero; a NULL passes (RDB-14)."""
    return CheckConstraint(f"{column} > 0", name=f"{column}_positive")


def ordered_range(
    low: str, high: str, *, name: str
) -> tuple[CheckConstraint, CheckConstraint]:
    """Keep an optional range in order, and its high end with a low.

    ``name`` is the range as a plural, such as ``"quantities"``. The
    high end alone is rejected: an exact value sets only the low end.
    """
    return (
        CheckConstraint(f"{high} >= {low}", name=f"{name}_in_order"),
        CheckConstraint(
            f"{high} IS NULL OR {low} IS NOT NULL", name=f"{high}_needs_{low}"
        ),
    )
