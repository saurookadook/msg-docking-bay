"""The columns every person table shares (ADR 0002)."""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from models.mixins.checks import not_empty, slug_format


class PersonDB:
    """Add a person's wiki title, names and slug, with their checks.

    For characters and mechanical designers: one row per person,
    however many works or suits they are linked to.
    """

    fandom_page_title: Mapped[str | None] = mapped_column(unique=True)
    """The Gundam Wiki page title; null when they have no page."""
    name: Mapped[str]
    """Not unique: people are told apart by ``slug``."""
    name_ja: Mapped[str | None]
    slug: Mapped[str] = mapped_column(unique=True)

    @declared_attr.directive
    @classmethod
    def __table_args__(cls) -> tuple[CheckConstraint, ...]:
        """Build the checks per table: a constraint has one table."""
        return (
            not_empty("fandom_page_title"),
            not_empty("name"),
            not_empty("name_ja"),
            slug_format(),
        )
