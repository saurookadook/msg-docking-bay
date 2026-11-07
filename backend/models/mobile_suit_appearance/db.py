"""The ``mobile_suit_appearances`` table: which works a suit is in."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, false
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import positive
from models.mixins.db import CreatedAtDB


class MobileSuitAppearanceDB(JunctionBaseDB, CreatedAtDB):
    """A mobile suit's appearance in one work, keyed on the pair.

    Pilot and operator links reference these rows through composite
    foreign keys (PR C), so "piloted in work W" implies the suit
    appears in W. Like every appearance, it cites its source.

    No constraint allows only one debut per suit: a suit can debut in
    a manga and an anime at once.
    """

    first_episode: Mapped[int | None]
    """The first episode it appears in; null for a film, or unknown."""
    is_debut: Mapped[bool] = mapped_column(server_default=false())
    last_episode: Mapped[int | None]
    mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    """Indexed: it does not lead the primary key (RDB-18)."""

    __table_args__ = (
        CheckConstraint("last_episode >= first_episode", name="episodes_in_order"),
        positive("first_episode"),
        CheckConstraint(
            "last_episode IS NULL OR first_episode IS NOT NULL",
            name="last_episode_needs_first",
        ),
    )
