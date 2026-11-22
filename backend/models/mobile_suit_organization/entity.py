"""Entities for ``mobile_suit_organizations`` (PYD-2, PYD-3)."""

import uuid

from constants.catalog import MobileSuitOrganizationRole
from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin, IdEntityMixin


class MobileSuitOrganizationEntity(
    BaseEntityModel, IdEntityMixin, CreatedAtEntityMixin
):
    """A row of ``mobile_suit_organizations``, as stored."""

    mobile_suit_id: uuid.UUID
    organization_id: uuid.UUID
    role: MobileSuitOrganizationRole
    source_id: uuid.UUID
    work_id: uuid.UUID | None = None
