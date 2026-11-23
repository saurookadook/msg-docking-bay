"""Entities for ``spec_sheet_materials`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from constants.catalog import MaterialUse
from models.base.entity import BaseEntityModel
from models.material.entity import MaterialRefEntity
from models.mixins.entity import CreatedAtEntityMixin


class SpecSheetMaterialEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A row of ``spec_sheet_materials``, as stored."""

    material_id: uuid.UUID
    material_use: MaterialUse
    note: str | None = None
    spec_sheet_id: uuid.UUID


class MaterialListingEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A material as one spec sheet lists it.

    Deliberately not the ``spec_sheet_materials`` row: the sheet's page
    needs the material's name and slug, not the listing's foreign keys
    (D5). There is no source: the sheet's covers the parts it lists
    (D6). ``created_at`` is the listing's, not the material's.
    """

    material_use: MaterialUse
    note: str | None = None
    """The infobox's ``~`` note on this entry, as written."""

    # ----- from `materials`, through `material_id`
    material: MaterialRefEntity
