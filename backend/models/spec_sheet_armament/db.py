"""The ``spec_sheet_armaments`` table: the armaments a sheet lists."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import ArmamentMount
from constants.db_types import ARMAMENT_MOUNT_DB_TYPE
from db.base_db import JunctionBaseDB
from models.mixins.checks import not_empty, ordered_range, positive
from models.mixins.db import CreatedAtDB


class SpecSheetArmamentDB(JunctionBaseDB, CreatedAtDB):
    """A weapon listed on a spec sheet, keyed on what it joins.

    ``mount`` is in the key, so one weapon can be listed as both
    fixed and handheld on a sheet.

    There is no ``source_id``: the sheet's source covers the parts it
    lists, the one exception to a source on every link (Phase 1).
    """

    armament_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("armaments.id", ondelete="RESTRICT"), primary_key=True
    )
    """RESTRICT: a weapon a sheet still lists cannot be deleted."""
    mount: Mapped[ArmamentMount] = mapped_column(
        ARMAMENT_MOUNT_DB_TYPE, primary_key=True
    )
    note: Mapped[str | None]
    """The infobox's ``~`` note on this entry, kept as written."""
    quantity_max: Mapped[int | None]
    quantity_min: Mapped[int | None]
    """The count before the item in the infobox; a range sets both."""
    spec_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("spec_sheets.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    """Indexed: it does not lead the primary key (RDB-18)."""

    __table_args__ = (
        not_empty("note"),
        *ordered_range("quantity_min", "quantity_max", name="quantities"),
        positive("quantity_min"),
    )
