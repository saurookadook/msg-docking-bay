"""Entities for ``mobile_suit_slug_redirects`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class MobileSuitSlugRedirectEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A suit's old slug, as stored."""

    mobile_suit_id: uuid.UUID
    old_slug: str
