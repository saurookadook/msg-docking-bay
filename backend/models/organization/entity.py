"""Entities for ``organizations`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from pydantic import Field

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin
from models.work.entity import CitedWorkEntity


class OrganizationEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """An organization row, as stored."""

    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: str
    parent_organization_id: uuid.UUID | None = None
    slug: str


class OrganizationRefEntity(BaseEntityModel):
    """Just enough of an organization to name and link it elsewhere."""

    name: str
    slug: str


class OrganizationCardEntity(BaseEntityModel, TimestampsEntityMixin):
    """One organization in a list.

    Deliberately not ``OrganizationEntity``: ``id`` and the wiki page
    keys are not public (D5). The parent is a ref, so a list costs no
    query per card.
    """

    name: str
    slug: str

    # ----- from `organizations`, through `parent_organization_id`
    parent_organization: OrganizationRefEntity | None = None


class OrganizationDetailEntity(OrganizationCardEntity):
    """An organization, with its units and the works it appears in.

    Leaves out its suits, which have their own paginated route: the
    Earth Federation alone operates hundreds (RDB-23).
    """

    # ----- from `organization_appearances`
    appearances: list[CitedWorkEntity] = Field(default_factory=list[CitedWorkEntity])
    # ----- from `organizations`, the rows whose parent this is
    child_organizations: list[OrganizationRefEntity] = Field(
        default_factory=list[OrganizationRefEntity]
    )
