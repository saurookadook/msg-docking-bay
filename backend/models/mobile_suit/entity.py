"""Entities for ``mobile_suits`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from pydantic import Field

from constants.catalog import (
    MobileSuitOrganizationRole,
    MobileSuitRelationType,
    UnitType,
)
from models.base.entity import BaseEntityModel
from models.character.entity import CharacterRefEntity
from models.continuity.entity import ContinuityRefEntity
from models.mechanical_designer.entity import MechanicalDesignerRefEntity
from models.mixins.entity import (
    CreatedAtEntityMixin,
    IdEntityMixin,
    TimestampsEntityMixin,
)
from models.organization.entity import OrganizationRefEntity
from models.source.entity import SourceCitationEntity
from models.spec_sheet.entity import MobileSuitSpecSheetEntity
from models.work.entity import WorkCardEntity, WorkRefEntity
from models.work_relation.entity import RelationDirection


class MobileSuitEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A mobile suit row, as stored."""

    continuity_id: uuid.UUID | None = None
    fandom_page_id: int | None = None
    model_number: str | None = None
    name: str
    name_ja: str | None = None
    slug: str
    unit_type: UnitType


class MobileSuitCardEntity(BaseEntityModel, TimestampsEntityMixin):
    """One suit in a list.

    Deliberately not the detail: loading spec sheets for fifty cards
    would cost an N+1 or a large join that nothing renders (D5). Leaves
    out ``id`` and ``fandom_page_id``: slugs are the public key.
    """

    model_number: str | None = None
    name: str
    name_ja: str | None = None
    slug: str
    unit_type: UnitType

    # ----- from `continuities`, through `continuity_id`
    continuity: ContinuityRefEntity | None = None


class MobileSuitAppearanceCardEntity(MobileSuitCardEntity):
    """A suit in one work's list, with how it appears there."""

    # ----- from `mobile_suit_appearances`
    first_episode: int | None = None
    is_debut: bool
    """True in the work the suit first appeared in."""
    last_episode: int | None = None


class PilotedMobileSuitEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A suit a character pilots, in one work or in a work not recorded.

    ``work`` is null when the page names no work for the pairing; such
    rows sort after the ones with a work.
    """

    # ----- from `mobile_suits`, through `mobile_suit_pilots`
    mobile_suit: MobileSuitCardEntity
    # ----- from `sources`, through `mobile_suit_pilots.source_id`
    source: SourceCitationEntity
    # ----- from `works`, through `mobile_suit_pilots.work_id`
    work: WorkRefEntity | None = None


class OrganizationLinkEntity(BaseEntityModel, CreatedAtEntityMixin):
    """One role an organization has for a suit, in one work or none."""

    role: MobileSuitOrganizationRole
    # ----- from `sources`, through the link's `source_id`
    source: SourceCitationEntity
    # ----- from `works`, through `mobile_suit_organizations.work_id`
    work: WorkRefEntity | None = None


class OrganizationMobileSuitEntity(BaseEntityModel):
    """A suit in an organization's list, with every role it has there.

    One item per suit, not per link, so a page of cards holds distinct
    suits; its links (one per role and work) are grouped in ``links``.
    """

    # ----- from `mobile_suits`
    mobile_suit: MobileSuitCardEntity
    # ----- from `mobile_suit_organizations`
    links: list[OrganizationLinkEntity] = Field(
        default_factory=list[OrganizationLinkEntity]
    )


class DesignedMobileSuitEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A suit in a designer's list, with the page crediting them."""

    # ----- from `mobile_suits`
    mobile_suit: MobileSuitCardEntity
    # ----- from `sources`, through `mobile_suit_designers.source_id`
    source: SourceCitationEntity


class RelatedMobileSuitEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A suit linked to the viewed one, read from the viewed one's side.

    Direct edges only: the whole family tree is a route of its own when
    a screen needs it (D5). ``created_at`` is when this database stored
    the edge, not when the wiki recorded it.
    """

    direction: RelationDirection
    relation_type: MobileSuitRelationType
    # ----- from `mobile_suits`, the edge's other end
    mobile_suit: MobileSuitCardEntity
    # ----- from `sources`, through `mobile_suit_relations.source_id`
    source: SourceCitationEntity


class WorkAppearanceEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A work the viewed suit appears in, with its episode range."""

    first_episode: int | None = None
    is_debut: bool
    last_episode: int | None = None
    # ----- from `sources`, through `mobile_suit_appearances.source_id`
    source: SourceCitationEntity
    # ----- from `works`, through `mobile_suit_appearances.work_id`
    work: WorkCardEntity


class PilotCreditEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A character who pilots the suit, in one work or in none."""

    # ----- from `characters`, through `mobile_suit_pilots.character_id`
    character: CharacterRefEntity
    # ----- from `sources`, through `mobile_suit_pilots.source_id`
    source: SourceCitationEntity
    # ----- from `works`, through `mobile_suit_pilots.work_id`
    work: WorkRefEntity | None = None


class OrganizationCreditEntity(BaseEntityModel, CreatedAtEntityMixin):
    """An organization's role for the suit, in one work or in none."""

    # ----- from `organizations`, through the link's `organization_id`
    organization: OrganizationRefEntity
    role: MobileSuitOrganizationRole
    # ----- from `sources`, through the link's `source_id`
    source: SourceCitationEntity
    # ----- from `works`, through the link's `work_id`
    work: WorkRefEntity | None = None


class DesignerCreditEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A mechanical designer credited with the suit."""

    # ----- from `mechanical_designers`, through the credit
    mechanical_designer: MechanicalDesignerRefEntity
    # ----- from `sources`, through `mobile_suit_designers.source_id`
    source: SourceCitationEntity


class MobileSuitDetailEntity(MobileSuitCardEntity):
    """A suit, with its sheets, relations, appearances and credits.

    Each nested list is read in one query, so a detail read costs the
    same few statements however many rows it holds (PYTEST-24). The
    people and organizations are refs: their own pages hold the rest
    (Q5). Parts join the spec sheets in a later PR.
    """

    # ----- from `mobile_suit_appearances`
    appearances: list[WorkAppearanceEntity] = Field(
        default_factory=list[WorkAppearanceEntity]
    )
    # ----- from `mobile_suit_designers`
    designers: list[DesignerCreditEntity] = Field(
        default_factory=list[DesignerCreditEntity]
    )
    # ----- from `mobile_suit_organizations`
    organizations: list[OrganizationCreditEntity] = Field(
        default_factory=list[OrganizationCreditEntity]
    )
    # ----- from `mobile_suit_pilots`
    pilots: list[PilotCreditEntity] = Field(default_factory=list[PilotCreditEntity])
    # ----- from `mobile_suit_relations`, in either direction
    relations: list[RelatedMobileSuitEntity] = Field(
        default_factory=list[RelatedMobileSuitEntity]
    )
    # ----- from `spec_sheets`
    spec_sheets: list[MobileSuitSpecSheetEntity] = Field(
        default_factory=list[MobileSuitSpecSheetEntity]
    )
