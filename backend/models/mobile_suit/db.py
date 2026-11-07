"""The ``mobile_suits`` table: one row per Gundam Wiki mobile weapon."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import UnitType
from constants.db_types import UNIT_TYPE_DB_TYPE
from db.base_db import BaseDB
from models.mixins.checks import not_empty, positive, slug_format
from models.mixins.db import TimestampsDB


class MobileSuitDB(BaseDB, TimestampsDB):
    """A mobile weapon, read from its own Gundam Wiki page.

    Versions such as the RX-78-2 and the RX-78-02 have pages of their
    own, so each is a row; ``mobile_suit_relations`` links them. Specs
    live in ``spec_sheets``, one per source and configuration.
    """

    continuity_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("continuities.id", ondelete="SET NULL"), index=True
    )
    """The timeline from the infobox ``era``; null when it has none."""
    fandom_page_id: Mapped[int | None] = mapped_column(unique=True)
    """The Gundam Wiki page ID, which survives a page rename."""
    model_number: Mapped[str | None]
    """The page title's prefix (``MS-06F``): the infobox has no field.

    Not unique: versions of one unit can share a model number.
    """
    name: Mapped[str]
    """Not unique: pages are told apart by ``slug`` and page ID."""
    name_ja: Mapped[str | None]
    slug: Mapped[str] = mapped_column(unique=True)
    unit_type: Mapped[UnitType] = mapped_column(UNIT_TYPE_DB_TYPE)

    __table_args__ = (
        positive("fandom_page_id"),
        not_empty("model_number"),
        not_empty("name"),
        not_empty("name_ja"),
        slug_format(),
    )
