"""Entities for ``spec_sheet_equipment`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from constants.catalog import EquipmentFit
from models.base.entity import BaseEntityModel
from models.equipment.entity import EquipmentRefEntity
from models.mixins.entity import CreatedAtEntityMixin


class SpecSheetEquipmentEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A row of ``spec_sheet_equipment``, as stored."""

    equipment_id: uuid.UUID
    fit: EquipmentFit
    note: str | None = None
    spec_sheet_id: uuid.UUID


class EquipmentListingEntity(BaseEntityModel, CreatedAtEntityMixin):
    """An item of equipment as one spec sheet lists it.

    Deliberately not the ``spec_sheet_equipment`` row: the sheet's page
    needs the item's name and slug, not the listing's foreign keys (D5).
    There is no source: the sheet's covers the parts it lists (D6).
    ``created_at`` is the listing's, not the item's.
    """

    fit: EquipmentFit
    note: str | None = None
    """The infobox's ``~`` note on this entry, as written."""

    # ----- from `equipment`, through `equipment_id`
    equipment: EquipmentRefEntity
