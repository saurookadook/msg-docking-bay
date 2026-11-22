"""Entities for ``mechanical_designers`` (PYD-2, PYD-3, PYD-4)."""

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin


class MechanicalDesignerEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A mechanical designer row, as stored."""

    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: str
    name_ja: str | None = None
    slug: str


class MechanicalDesignerRefEntity(BaseEntityModel):
    """Just enough of a designer to name and link them elsewhere."""

    name: str
    slug: str


class MechanicalDesignerCardEntity(BaseEntityModel, TimestampsEntityMixin):
    """One mechanical designer in a list.

    Deliberately not ``MechanicalDesignerEntity``: ``id`` and the wiki
    page keys are not public (D5).
    """

    name: str
    name_ja: str | None = None
    slug: str


class MechanicalDesignerDetailEntity(MechanicalDesignerCardEntity):
    """A mechanical designer, on their own page.

    It holds only the card's fields today. Their suits are a paginated
    route of their own, since one designer can have hundreds (Q1,
    RDB-23). A separate type keeps the page's contract apart from the
    list's, so a field added to the page leaves the cards unchanged.
    """
