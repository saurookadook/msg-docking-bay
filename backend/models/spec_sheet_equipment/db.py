"""The ``spec_sheet_equipment`` table: the equipment a sheet lists."""

import uuid
from typing import override

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from constants.catalog import EquipmentFit
from constants.db_types import EQUIPMENT_FIT_DB_TYPE
from db.base_db import JunctionBaseDB
from models.mixins.checks import not_empty
from models.mixins.db import CreatedAtDB


class SpecSheetEquipmentDB(JunctionBaseDB, CreatedAtDB):
    """An item listed on a spec sheet, keyed on what it joins.

    ``fit`` is in the key, so an item can be listed as standard
    and optional on one sheet.

    There is no ``source_id``: the sheet's source covers the parts it
    lists, the one exception to a source on every link (Phase 1).
    """

    @declared_attr.directive
    @classmethod
    @override
    def __tablename__(cls) -> str:
        """Use the mass noun, as ``equipment`` does."""
        return "spec_sheet_equipment"

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("equipment.id", ondelete="RESTRICT"), primary_key=True
    )
    """RESTRICT: an item a sheet still lists cannot be deleted."""
    fit: Mapped[EquipmentFit] = mapped_column(EQUIPMENT_FIT_DB_TYPE, primary_key=True)
    note: Mapped[str | None]
    """The infobox's ``~`` note on this entry, kept as written."""
    spec_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("spec_sheets.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    """Indexed: it does not lead the primary key (RDB-18)."""

    __table_args__ = (not_empty("note"),)
