"""The ``mobile_suit_pilots`` table: who pilots a suit, and where."""

import uuid

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.db import CreatedAtDB


class MobileSuitPilotDB(BaseDB, CreatedAtDB):
    """A character piloting a mobile suit, in one work or in none.

    A deliberate deviation from RDB-2: a three-way link with an
    optional ``work_id`` cannot key on its foreign keys, since a
    primary key column is never null. So it has a surrogate ``id`` and
    a ``UNIQUE NULLS NOT DISTINCT`` key (PostgreSQL 15+), which allows
    one "work unknown" row per pilot and suit.

    Two composite foreign keys tie a row to the appearances, so
    "piloted in work W" implies the character and the suit both appear
    in W. They are MATCH SIMPLE: a null ``work_id`` skips them whole,
    so plain foreign keys check the character and the suit as well.
    """

    character_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE")
    )
    """Led by the (character, work) index, so not indexed alone."""
    mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE")
    )
    """Led by the (suit, work) index, so not indexed alone."""
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    work_id: Mapped[uuid.UUID | None]
    """The work they pilot it in; null when the page does not say."""

    __table_args__ = (
        # CASCADE: a pilot link needs both appearances it relies on.
        ForeignKeyConstraint(
            ["character_id", "work_id"],
            [
                "character_appearances.character_id",
                "character_appearances.work_id",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["mobile_suit_id", "work_id"],
            [
                "mobile_suit_appearances.mobile_suit_id",
                "mobile_suit_appearances.work_id",
            ],
            ondelete="CASCADE",
        ),
        # Named here: the ix convention repeats the table name for
        # each column of a multi-column index.
        Index("ix_mobile_suit_pilots_character_id_work_id", "character_id", "work_id"),
        Index(
            "ix_mobile_suit_pilots_mobile_suit_id_work_id",
            "mobile_suit_id",
            "work_id",
        ),
        UniqueConstraint(
            "character_id",
            "mobile_suit_id",
            "work_id",
            postgresql_nulls_not_distinct=True,
        ),
    )
