"""The ``spec_sheet_materials`` table: the materials a sheet lists."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import MaterialUse
from constants.db_types import MATERIAL_USE_DB_TYPE
from db.base_db import JunctionBaseDB
from models.mixins.checks import not_empty
from models.mixins.db import CreatedAtDB


class SpecSheetMaterialDB(JunctionBaseDB, CreatedAtDB):
    """A material listed on a spec sheet, keyed on what it joins.

    ``material_use`` is in the key, so one material can be listed
    as both armor and frame on a sheet.

    There is no ``source_id``: the sheet's source covers the parts it
    lists, the one exception to a source on every link (Phase 1).
    """

    material_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("materials.id", ondelete="RESTRICT"), primary_key=True
    )
    """RESTRICT: a material a sheet still lists cannot be deleted."""
    material_use: Mapped[MaterialUse] = mapped_column(
        MATERIAL_USE_DB_TYPE, primary_key=True
    )
    note: Mapped[str | None]
    """The infobox's ``~`` note on this entry, kept as written."""
    spec_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("spec_sheets.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    """Indexed: it does not lead the primary key (RDB-18)."""

    __table_args__ = (not_empty("note"),)
