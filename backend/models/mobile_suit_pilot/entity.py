"""Entities for ``mobile_suit_pilots`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin, IdEntityMixin


class MobileSuitPilotEntity(BaseEntityModel, IdEntityMixin, CreatedAtEntityMixin):
    """A row of ``mobile_suit_pilots``, as stored."""

    character_id: uuid.UUID
    mobile_suit_id: uuid.UUID
    source_id: uuid.UUID
    work_id: uuid.UUID | None = None
