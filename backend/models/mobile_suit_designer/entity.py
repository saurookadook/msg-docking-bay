"""Entities for ``mobile_suit_designers`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class MobileSuitDesignerEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A row of ``mobile_suit_designers``, as stored."""

    mechanical_designer_id: uuid.UUID
    mobile_suit_id: uuid.UUID
    source_id: uuid.UUID
