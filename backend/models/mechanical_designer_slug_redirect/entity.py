"""Entities for ``mechanical_designer_slug_redirects`` (PYD-2)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class MechanicalDesignerSlugRedirectEntity(BaseEntityModel, CreatedAtEntityMixin):
    """An old slug, as stored."""

    mechanical_designer_id: uuid.UUID
    old_slug: str
