"""The ``equipment`` table: parts that spec sheets list."""

from typing import override

from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty, slug_format
from models.mixins.db import TimestampsDB


class EquipmentDB(BaseDB, TimestampsDB):
    """Equipment with its own wiki page, such as the Core Block System.

    One row however many suits carry it (ADR 0002).
    """

    @declared_attr.directive
    @classmethod
    @override
    def __tablename__(cls) -> str:
        """Use the mass noun: the derived ``equipments`` is wrong."""
        return "equipment"

    fandom_page_title: Mapped[str | None] = mapped_column(unique=True)
    """The Gundam Wiki page title; null when it has no page."""
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)

    __table_args__ = (
        not_empty("fandom_page_title"),
        not_empty("name"),
        slug_format(),
    )
