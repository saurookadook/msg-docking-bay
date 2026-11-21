"""Entities for ``work_slug_redirects`` (PYD-2, PYD-3)."""

import uuid

from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class WorkSlugRedirectEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A work's old slug, as stored."""

    old_slug: str
    work_id: uuid.UUID
