"""Entities for ``works`` (PYD-2, PYD-3, PYD-4)."""

import uuid
from datetime import date

from pydantic import Field

from constants.catalog import WorkRelationType, WorkType
from models.base.entity import BaseEntityModel
from models.continuity.entity import ContinuityRefEntity
from models.mixins.entity import (
    CreatedAtEntityMixin,
    IdEntityMixin,
    TimestampsEntityMixin,
)
from models.source.entity import SourceCitationEntity
from models.work_relation.entity import RelationDirection


class WorkEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A work row, as stored."""

    anilist_id: int | None = None
    ann_id: int | None = None
    continuity_id: uuid.UUID | None = None
    end_date: date | None = None
    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    parent_work_id: uuid.UUID | None = None
    slug: str
    start_date: date | None = None
    title: str
    title_ja: str | None = None
    wikidata_qid: str | None = None
    work_type: WorkType


class WorkRefEntity(BaseEntityModel):
    """Just enough of a work to name and link it from another work."""

    slug: str
    title: str


class WorkCardEntity(BaseEntityModel, TimestampsEntityMixin):
    """One work in a list.

    Deliberately not ``WorkEntity``: a list renders no external IDs, and
    ``id`` is not a public key (D5). Relations are on the detail only.
    """

    end_date: date | None = None
    slug: str
    start_date: date | None = None
    title: str
    title_ja: str | None = None
    work_type: WorkType

    # ----- from `continuities`, through `continuity_id`
    continuity: ContinuityRefEntity | None = None


class RelatedWorkEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A work linked to the viewed one, read from the viewed one's side.

    ``created_at`` is when this database stored the edge; the source's
    ``revision_id`` says which copy of the page it came from (D5, D6).
    """

    direction: RelationDirection
    relation_type: WorkRelationType
    # ----- from `sources`, through `work_relations.source_id`
    source: SourceCitationEntity
    # ----- from `works`, the edge's other end
    work: WorkCardEntity


class WorkDetailEntity(WorkCardEntity):
    """A work, with its parent and every work it is directly linked to.

    Leaves out external IDs and ``id`` (D5), and the work's suits, which
    have their own paginated route.
    """

    # ----- from `works`, through `parent_work_id`
    parent_work: WorkRefEntity | None = None
    # ----- from `work_relations`, in either direction
    relations: list[RelatedWorkEntity] = Field(default_factory=list[RelatedWorkEntity])
