"""Entities for ``characters`` (PYD-2, PYD-3, PYD-4)."""

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin


class CharacterEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A character row, as stored."""

    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: str
    name_ja: str | None = None
    slug: str


class CharacterRefEntity(BaseEntityModel):
    """Just enough of a character to name and link them elsewhere."""

    name: str
    slug: str


class CharacterCardEntity(BaseEntityModel, TimestampsEntityMixin):
    """One character in a list.

    Deliberately not ``CharacterEntity``: ``id`` and the wiki page keys
    are not public (D5). Appearances and piloted suits are on the
    detail only (``models.character.detail``).
    """

    name: str
    name_ja: str | None = None
    slug: str
