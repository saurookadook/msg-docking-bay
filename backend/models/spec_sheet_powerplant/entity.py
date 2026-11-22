"""Entities for ``spec_sheet_powerplants`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin
from models.powerplant.entity import PowerplantRefEntity


class SpecSheetPowerplantEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A row of ``spec_sheet_powerplants``, as stored."""

    note: str | None = None
    powerplant_id: uuid.UUID
    quantity_max: int | None = None
    quantity_min: int | None = None
    spec_sheet_id: uuid.UUID


class PowerplantListingEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A powerplant as one spec sheet lists it.

    Deliberately not the ``spec_sheet_powerplants`` row: the sheet's
    page needs the powerplant's name and slug, not the listing's foreign
    keys (D5). There is no source: the sheet's covers the parts it lists
    (D6). ``created_at`` is the listing's, not the powerplant's.
    """

    note: str | None = None
    """The infobox's ``~`` note on this entry, as written."""
    quantity_max: int | None = None
    quantity_min: int | None = None
    """The count before the item in the infobox; null when none."""

    # ----- from `powerplants`, through `powerplant_id`
    powerplant: PowerplantRefEntity
