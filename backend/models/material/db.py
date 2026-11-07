"""The ``materials`` table: parts that spec sheets list."""

from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty, slug_format
from models.mixins.db import TimestampsDB


class MaterialDB(BaseDB, TimestampsDB):
    """An armor or frame material, such as Luna Titanium Alloy.

    One row however many suits use it (ADR 0002).
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
