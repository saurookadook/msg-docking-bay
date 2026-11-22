"""Entities for ``equipment`` (PYD-2, PYD-4)."""

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin


class EquipmentEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """An item of equipment row, as stored."""

    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: str
    slug: str


class EquipmentRefEntity(BaseEntityModel):
    """Just enough of an item of equipment to name and link it.

    Leaves out ``id``, the wiki page keys and the row's timestamps: none
    is public or rendered on a sheet (D5). A card waits for a part list
    route.
    """

    name: str
    slug: str
