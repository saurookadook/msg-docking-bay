"""The columns every spec sheet part table shares (ADR 0002)."""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from models.mixins.checks import not_empty, slug_format


class PartDB:
    """Add a part's wiki title, name and slug, with their checks.

    For armaments, equipment, materials and powerplants: one row per
    part, however many sheets list it.
    """

    fandom_page_title: Mapped[str | None] = mapped_column(unique=True)
    """The Gundam Wiki page title; null when it has no page."""
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)

    @declared_attr.directive
    @classmethod
    def __table_args__(cls) -> tuple[CheckConstraint, ...]:
        """Build the checks per table: a constraint has one table."""
        return (not_empty("fandom_page_title"), not_empty("name"), slug_format())
