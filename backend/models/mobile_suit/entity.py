"""Entities for ``mobile_suits`` (PYD-2, PYD-3, PYD-4)."""

import uuid

from pydantic import Field

from constants.catalog import MobileSuitRelationType, UnitType
from models.base.entity import BaseEntityModel
from models.continuity.entity import ContinuityRefEntity
from models.mixins.entity import (
    CreatedAtEntityMixin,
    IdEntityMixin,
    TimestampsEntityMixin,
)
from models.source.entity import SourceCitationEntity
from models.spec_sheet.entity import MobileSuitSpecSheetEntity
from models.work.entity import WorkCardEntity
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


class MobileSuitDetailEntity(MobileSuitCardEntity):
    """A suit, with its spec sheets, direct relations and appearances.

    Each nested list is read in one query, so a detail read costs the
    same few statements however many rows it holds (PYTEST-24). Parts
    join the spec sheets in a later PR; pilots and organizations too.
    """

    # ----- from `mobile_suit_appearances`
    appearances: list[WorkAppearanceEntity] = Field(
        default_factory=list[WorkAppearanceEntity]
    )
    # ----- from `mobile_suit_relations`, in either direction
    relations: list[RelatedMobileSuitEntity] = Field(
        default_factory=list[RelatedMobileSuitEntity]
    )
    # ----- from `spec_sheets`
    spec_sheets: list[MobileSuitSpecSheetEntity] = Field(
        default_factory=list[MobileSuitSpecSheetEntity]
    )
