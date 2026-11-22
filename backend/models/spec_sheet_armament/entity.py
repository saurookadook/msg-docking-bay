"""Entities for ``spec_sheet_armaments`` (PYD-2, PYD-4)."""

from constants.catalog import ArmamentMount
from models.armament.entity import ArmamentRefEntity
from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class ArmamentListingEntity(BaseEntityModel, CreatedAtEntityMixin):
    """An armament as one spec sheet lists it.

    Deliberately not the ``spec_sheet_armaments`` row: the sheet's page
    needs the weapon's name and slug, not the listing's foreign keys
    (D5). There is no source: the sheet's covers the parts it lists
    (D6). ``created_at`` is the listing's, not the weapon's.
    """

    mount: ArmamentMount
    note: str | None = None
    """The infobox's ``~`` note on this entry, as written."""
    quantity_max: int | None = None
    quantity_min: int | None = None
    """The count before the item in the infobox; null when none."""

    # ----- from `armaments`, through `armament_id`
    armament: ArmamentRefEntity
