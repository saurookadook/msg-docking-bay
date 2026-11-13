"""The ``mobile_suit_designers`` table: who designed each suit."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.db import CreatedAtDB


class MobileSuitDesignerDB(JunctionBaseDB, CreatedAtDB):
    """A mechanical designer credited with a mobile suit's design.

    Keyed on the pair (RDB-2). A designer a suit still credits cannot
    be deleted; deleting the suit removes its credits. Like every
    edge, it cites its source.
    """

    mechanical_designer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mechanical_designers.id", ondelete="RESTRICT"), primary_key=True
    )
    """RESTRICT: a credited designer cannot be deleted (RDB-15)."""
    mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    """Indexed: it does not lead the primary key (RDB-18)."""
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
