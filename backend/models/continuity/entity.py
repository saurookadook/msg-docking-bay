"""Entities for ``continuities`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin


class ContinuityEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A continuity row, as stored."""

    name: str
    parent_continuity_id: uuid.UUID | None = None
    slug: str


class ContinuityRefEntity(BaseEntityModel):
    """Just enough of a continuity to name and link it from a card.

    Deliberately not a card: nesting full cards inside other cards
    would make every list load a chain of rows.
    """

    name: str
    slug: str


class ContinuityCardEntity(BaseEntityModel, TimestampsEntityMixin):
    """One continuity in the list of every continuity.

    Leaves out ``id``: slugs are the public key (D2, D5).
    """

    name: str
    slug: str

    # ----- from `continuities`, through `parent_continuity_id`
    parent_continuity: ContinuityRefEntity | None = None
