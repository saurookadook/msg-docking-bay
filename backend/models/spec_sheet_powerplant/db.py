"""The ``spec_sheet_powerplants`` table: a sheet's generators."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import not_empty, ordered_range, positive
from models.mixins.db import CreatedAtDB


class SpecSheetPowerplantDB(JunctionBaseDB, CreatedAtDB):
    """A powerplant listed on a spec sheet, keyed on what it joins.

    There is no ``source_id``: the sheet's source covers the parts it
    lists, the one exception to a source on every link (Phase 1).
    """

    note: Mapped[str | None]
    """The infobox's ``~`` note on this entry, kept as written."""
    powerplant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("powerplants.id", ondelete="RESTRICT"), primary_key=True
    )
    """RESTRICT: a powerplant a sheet still lists cannot be deleted."""
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
