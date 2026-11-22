"""Entities for ``organization_appearances`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class OrganizationAppearanceEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A row of ``organization_appearances``, as stored."""

    organization_id: uuid.UUID
    source_id: uuid.UUID
    work_id: uuid.UUID
