"""The ``continuities`` table: Gundam timelines such as the UC."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty, not_own_parent, slug_format
from models.mixins.db import TimestampsDB


class ContinuityDB(BaseDB, TimestampsDB):
    """A timeline, seeded from the Gundam Wiki's infobox ``era`` values.

    A lookup table rather than an enum, because new timelines arrive
    without a code change (RDB-6).
    """

    name: Mapped[str] = mapped_column(unique=True)
    parent_continuity_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("continuities.id", ondelete="SET NULL"), index=True
    )
    """The timeline this one branches from: GQ's alternate UC → UC."""
    slug: Mapped[str] = mapped_column(unique=True)

    __table_args__ = (
        not_empty("name"),
        not_own_parent("parent_continuity_id"),
        slug_format(),
    )
