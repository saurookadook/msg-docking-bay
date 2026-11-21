"""Entities for ``mobile_suit_appearances`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class MobileSuitAppearanceEntity(BaseEntityModel, CreatedAtEntityMixin):
    """An appearance row, as stored."""

    first_episode: int | None = None
    is_debut: bool
    last_episode: int | None = None
    mobile_suit_id: uuid.UUID
    source_id: uuid.UUID
    work_id: uuid.UUID
