"""The ``armaments`` table: parts that spec sheets list."""

from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty, slug_format
from models.mixins.db import TimestampsDB


class ArmamentDB(BaseDB, TimestampsDB):
    """A weapon with its own wiki page, such as the 60mm Vulcan Gun.

    One row however many suits carry it, so its page can list
    every sheet that does (ADR 0002).
    """

    fandom_page_title: Mapped[str | None] = mapped_column(unique=True)
    """The Gundam Wiki page title; null when it has no page."""
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)

    __table_args__ = (
        not_empty("fandom_page_title"),
        not_empty("name"),
        slug_format(),
    )
