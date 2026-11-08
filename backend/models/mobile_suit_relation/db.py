"""The ``mobile_suit_relations`` table: lineage edges between suits."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import MobileSuitRelationType
from constants.db_types import MOBILE_SUIT_RELATION_TYPE_DB_TYPE
from db.base_db import JunctionBaseDB
from models.mixins.db import CreatedAtDB


class MobileSuitRelationDB(JunctionBaseDB, CreatedAtDB):
    """A directed edge: "``from`` is a ``relation_type`` of ``to``".

    Families such as the Zaku and GM lines are walked with a recursive
    query over these edges; no graph extension is used (ADR 0002). The
    key is the edge itself (RDB-2), so a pair of suits may be linked by
    several types but by each type only once. Like every edge, it cites
    the page it was read from.
    """

    from_mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE"), primary_key=True
    )
    relation_type: Mapped[MobileSuitRelationType] = mapped_column(
        MOBILE_SUIT_RELATION_TYPE_DB_TYPE, primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    to_mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    """Indexed: it does not lead the primary key (RDB-18)."""

    __table_args__ = (
        CheckConstraint(
            "from_mobile_suit_id <> to_mobile_suit_id", name="not_self_relation"
        ),
    )
