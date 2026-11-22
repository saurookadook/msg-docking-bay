"""Entities for ``organization_slug_redirects`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class OrganizationSlugRedirectEntity(BaseEntityModel, CreatedAtEntityMixin):
    """An old slug, as stored."""

    organization_id: uuid.UUID
    old_slug: str
