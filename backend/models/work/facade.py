"""Data access for ``works`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import ColumnElement, case, func, or_, select
from sqlalchemy.orm import aliased, joinedload

from constants.catalog import WorkType
from models.base.facade import BaseFacade
from models.base.page import Page
from models.continuity.db import ContinuityDB
from models.source.entity import SourceCitationEntity
from models.work.db import WorkDB
from models.work.entity import (
    RelatedWorkEntity,
    WorkCardEntity,
    WorkDetailEntity,
    WorkEntity,
    WorkRefEntity,
)
from models.work_relation.db import WorkRelationDB
from models.work_relation.entity import WorkRelationEntity
from models.work_slug_redirect.db import WorkSlugRedirectDB
from models.work_slug_redirect.entity import WorkSlugRedirectEntity


class WorkFacade(BaseFacade):
    """Read and write works, their relations, and their old slugs."""

    class NotFoundError(Exception):
        """No work has the slug, as a current or an old one."""

    def get_page(
        self,
        *,
        continuity_slug: str | None = None,
        work_type: WorkType | None = None,
        limit: int,
        offset: int,
    ) -> Page[WorkCardEntity]:
        """Return one page of works, first released first (D3).

        Works with no known date come last. Filters match current slugs
        only: an unknown continuity gives an empty page, not an error.
        """
        filters: list[ColumnElement[bool]] = []
        if continuity_slug is not None:
            filters.append(
                WorkDB.continuity_id.in_(
                    select(ContinuityDB.id).where(ContinuityDB.slug == continuity_slug)
                )
            )
        if work_type is not None:
            filters.append(WorkDB.work_type == work_type)

        works = self.db_session.scalars(
            select(WorkDB)
            .options(joinedload(WorkDB.continuity))
            .where(*filters)
            .order_by(WorkDB.start_date.asc().nulls_last(), WorkDB.title, WorkDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(WorkDB).where(*filters)
        ).scalar_one()
        return Page[WorkCardEntity](
            items=[WorkCardEntity.model_validate(work) for work in works], total=total
        )

    def get_id_by_slug(self, slug: str) -> uuid.UUID:
        """Return the ID of the work with this current or old slug (D2).

        Raises:
            WorkFacade.NotFoundError: when neither matches.
        """
        work_id = self.db_session.scalars(
            select(WorkDB.id)
            .where(self._has_slug(slug))
            .order_by(self._current_slug_first(slug))
            .limit(1)
        ).first()
        if work_id is None:
            raise WorkFacade.NotFoundError(
                f"Work record with ``slug='{slug}'`` not found"
            )
        return work_id

    def get_one_by_slug(self, slug: str) -> WorkDetailEntity:
        """Return a work, with its parent and relations, by any slug.

        An old slug finds the renamed work, whose ``slug`` field then
        holds the current one (D2). Two queries, however many relations.

        Raises:
            WorkFacade.NotFoundError: when no work has the slug.
        """
        work = self.db_session.scalars(
            select(WorkDB)
            .options(joinedload(WorkDB.continuity), joinedload(WorkDB.parent_work))
            .where(self._has_slug(slug))
            .order_by(self._current_slug_first(slug))
            .limit(1)
        ).first()
        if work is None:
            raise WorkFacade.NotFoundError(
                f"Work record with ``slug='{slug}'`` not found"
            )

        card = WorkCardEntity.model_validate(work)
        parent = work.parent_work
        return WorkDetailEntity.model_validate(
            {
                **card.model_dump(),
                "parent_work": None
                if parent is None
                else WorkRefEntity.model_validate(parent),
                "relations": self._get_relations(work.id),
            }
        )

    def create_or_update(self, *, payload: Mapping[str, Any]) -> WorkEntity:
        """Upsert a work on its slug (SQLA-25)."""
        work = self._upsert(WorkDB, payload=payload, conflict_columns=["slug"])
        return WorkEntity.model_validate(work)

    def create_or_update_relation(
        self, *, payload: Mapping[str, Any]
    ) -> WorkRelationEntity:
        """Upsert a relation on its edge, updating only its source."""
        relation = self._upsert(
            WorkRelationDB,
            payload=payload,
            conflict_columns=["from_work_id", "relation_type", "to_work_id"],
        )
        return WorkRelationEntity.model_validate(relation)

    def create_or_update_slug_redirect(
        self, *, payload: Mapping[str, Any]
    ) -> WorkSlugRedirectEntity:
        """Upsert an old slug, pointing it at a work (D2)."""
        redirect = self._upsert(
            WorkSlugRedirectDB, payload=payload, conflict_columns=["old_slug"]
        )
        return WorkSlugRedirectEntity.model_validate(redirect)

    @staticmethod
    def _has_slug(slug: str) -> ColumnElement[bool]:
        """Match the work whose current or old slug this is."""
        return or_(
            WorkDB.slug == slug,
            WorkDB.id.in_(
                select(WorkSlugRedirectDB.work_id).where(
                    WorkSlugRedirectDB.old_slug == slug
                )
            ),
        )

    @staticmethod
    def _current_slug_first(slug: str) -> ColumnElement[int]:
        """Rank a current slug before an old one (D2)."""
        return case((WorkDB.slug == slug, 0), else_=1)

    def _get_relations(self, work_id: uuid.UUID) -> list[RelatedWorkEntity]:
        """Return every edge that touches the work, from its side (D5).

        Ordered by type, then direction, then the other work's title.
        """
        other = aliased(WorkDB)
        is_outgoing = WorkRelationDB.from_work_id == work_id
        direction = case((is_outgoing, "outgoing"), else_="incoming").label("direction")
        other_id = case(
            (is_outgoing, WorkRelationDB.to_work_id), else_=WorkRelationDB.from_work_id
        )
        rows = self.db_session.execute(
            select(WorkRelationDB, other, direction)
            .join(other, other.id == other_id)
            .where(or_(is_outgoing, WorkRelationDB.to_work_id == work_id))
            .options(joinedload(WorkRelationDB.source), joinedload(other.continuity))
            .order_by(WorkRelationDB.relation_type, direction, other.title, other.slug)
        ).all()
        return [
            RelatedWorkEntity.model_validate(
                {
                    "created_at": relation.created_at,
                    "direction": row_direction,
                    "relation_type": relation.relation_type,
                    "source": SourceCitationEntity.model_validate(relation.source),
                    "work": WorkCardEntity.model_validate(other_work),
                }
            )
            for relation, other_work, row_direction in rows
        ]
