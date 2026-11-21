"""Entities for ``mobile_suit_relations`` (PYD-2, PYD-3)."""

import uuid

from constants.catalog import MobileSuitRelationType
from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class MobileSuitRelationEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A relation row, as stored: "``from`` is a type of ``to``"."""

    from_mobile_suit_id: uuid.UUID
    relation_type: MobileSuitRelationType
    source_id: uuid.UUID
    to_mobile_suit_id: uuid.UUID
