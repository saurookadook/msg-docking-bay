"""Entities for ``materials`` (PYD-2, PYD-4)."""

from models.base.entity import BaseEntityModel


class MaterialRefEntity(BaseEntityModel):
    """Just enough of a material to name and link it.

    Leaves out ``id``, the wiki page keys and the row's timestamps: none
    is public or rendered on a sheet (D5). A card waits for a part list
    route.
    """

    name: str
    slug: str
