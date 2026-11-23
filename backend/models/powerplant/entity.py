"""Entities for ``powerplants`` (PYD-2, PYD-4)."""

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin


class PowerplantEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A powerplant row, as stored."""

    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: str
    slug: str


class PowerplantRefEntity(BaseEntityModel):
    """Just enough of a powerplant to name and link it.

    Leaves out ``id``, the wiki page keys and the row's timestamps: none
    is public or rendered on a sheet (D5). A card waits for a part list
    route.
    """

    name: str
    slug: str
