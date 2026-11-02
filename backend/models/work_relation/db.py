"""The ``work_relations`` table: sequels, compilations, remakes."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import WorkRelationType
from constants.db_types import WORK_RELATION_TYPE_DB_TYPE
from db.base_db import JunctionBaseDB
from models.mixins.db import CreatedAtDB


class WorkRelationDB(JunctionBaseDB, CreatedAtDB):
    """A directed edge: "``from`` is a ``relation_type`` of ``to``".

    The key is the edge itself (RDB-2), so a pair of works may be linked
    by several types but by each type only once. Like every edge, it
    cites the page it was read from (ADR 0002).
    """

    from_work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), primary_key=True
    )
    relation_type: Mapped[WorkRelationType] = mapped_column(
        WORK_RELATION_TYPE_DB_TYPE, primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    to_work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    """Indexed: it does not lead the primary key (RDB-18)."""

    __table_args__ = (
        CheckConstraint("from_work_id <> to_work_id", name="not_self_relation"),
    )
