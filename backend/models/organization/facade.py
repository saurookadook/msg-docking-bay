"""Data access for ``organizations`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import contains_eager, joinedload

from constants.catalog import MobileSuitOrganizationRole
from models.base.facade import BaseFacade, normalize_search
from models.base.page import Page
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import (
    MobileSuitCardEntity,
    OrganizationLinkEntity,
    OrganizationMobileSuitEntity,
)
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.organization.db import OrganizationDB
from models.organization.entity import (
    OrganizationCardEntity,
    OrganizationDetailEntity,
    OrganizationEntity,
    OrganizationRefEntity,
)
from models.organization_appearance.db import OrganizationAppearanceDB
from models.organization_appearance.entity import OrganizationAppearanceEntity
from models.organization_slug_redirect.db import OrganizationSlugRedirectDB
from models.organization_slug_redirect.entity import OrganizationSlugRedirectEntity
from models.source.entity import SourceCitationEntity
from models.work.db import WorkDB
from models.work.entity import CitedWorkEntity, WorkCardEntity
from models.work.facade import optional_work_ref


class OrganizationFacade(BaseFacade):
    """Read and write organizations, their appearances and old slugs."""

    class NotFoundError(Exception):
        """No organization has the slug, as a current or an old one."""

    def get_page(
        self,
        *,
        work_slug: str | None = None,
        q: str | None = None,
        limit: int,
        offset: int,
    ) -> Page[OrganizationCardEntity]:
        """Return one page of organizations, by name (D3).

        ``q`` matches the normalized slug, prefix matches first (D8).
        ``work_slug`` matches current slugs only: an unknown work gives
        an empty page.
        """
        filters: list[ColumnElement[bool]] = []
        if work_slug is not None:
            filters.append(
                OrganizationDB.id.in_(
                    select(OrganizationAppearanceDB.organization_id)
                    .join(WorkDB, WorkDB.id == OrganizationAppearanceDB.work_id)
                    .where(WorkDB.slug == work_slug)
                )
            )
        order: list[ColumnElement[Any]] = []
        needle = normalize_search(q)
        if needle is not None:
            filters.append(self._search_filter((OrganizationDB.slug,), needle))
            order.append(self._prefix_rank((OrganizationDB.slug,), needle))

        organizations = self.db_session.scalars(
            select(OrganizationDB)
            .options(joinedload(OrganizationDB.parent_organization))
            .where(*filters)
            .order_by(*order, OrganizationDB.name, OrganizationDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(OrganizationDB).where(*filters)
        ).scalar_one()
        return Page[OrganizationCardEntity](
            items=[OrganizationCardEntity.model_validate(row) for row in organizations],
            total=total,
        )

    def get_id_by_slug(self, slug: str) -> uuid.UUID:
        """Return the ID of an organization by its current or old slug.

        Raises:
            OrganizationFacade.NotFoundError: when neither matches.
        """
        organization_id = self.db_session.scalars(
            select(OrganizationDB.id)
            .where(self._organization_has_slug(slug))
            .order_by(self._current_slug_first(OrganizationDB.slug, slug))
            .limit(1)
        ).first()
        if organization_id is None:
            raise OrganizationFacade.NotFoundError(
                f"Organization record with ``slug='{slug}'`` not found"
            )
        return organization_id

    def get_one_by_slug(self, slug: str) -> OrganizationDetailEntity:
        """Return an organization with its parent, units and works.

        An old slug finds the renamed organization (D2). Three
        statements, however many rows the lists hold (PYTEST-24).

        Raises:
            OrganizationFacade.NotFoundError: when no slug matches.
        """
        organization = self.db_session.scalars(
            select(OrganizationDB)
            .options(joinedload(OrganizationDB.parent_organization))
            .where(self._organization_has_slug(slug))
            .order_by(self._current_slug_first(OrganizationDB.slug, slug))
            .limit(1)
        ).first()
        if organization is None:
            raise OrganizationFacade.NotFoundError(
                f"Organization record with ``slug='{slug}'`` not found"
            )
        children = self.db_session.scalars(
            select(OrganizationDB)
            .where(OrganizationDB.parent_organization_id == organization.id)
            .order_by(OrganizationDB.name, OrganizationDB.slug)
        ).all()
        return OrganizationDetailEntity.model_validate(
            {
                **OrganizationCardEntity.model_validate(organization).model_dump(),
                "appearances": self._get_appearances(organization.id),
                "child_organizations": [
                    OrganizationRefEntity.model_validate(child) for child in children
                ],
            }
        )

    def get_mobile_suit_page(
        self,
        slug: str,
        *,
        role: MobileSuitOrganizationRole | None = None,
        limit: int,
        offset: int,
    ) -> Page[OrganizationMobileSuitEntity]:
        """Return one page of an organization's suits, by name.

        One item per suit, with its links grouped; ``total`` counts
        suits. ``role`` keeps only suits with a link in that role, and
        only those links. Four statements: the slug, the page, the count
        and the links (PYTEST-24).

        Raises:
            OrganizationFacade.NotFoundError: when no slug matches.
        """
        organization_id = self.get_id_by_slug(slug)
        link_filters: list[ColumnElement[bool]] = [
            MobileSuitOrganizationDB.organization_id == organization_id
        ]
        if role is not None:
            link_filters.append(MobileSuitOrganizationDB.role == role)
        in_organization = MobileSuitDB.id.in_(
            select(MobileSuitOrganizationDB.mobile_suit_id).where(*link_filters)
        )

        suits = self.db_session.scalars(
            select(MobileSuitDB)
            .options(joinedload(MobileSuitDB.continuity))
            .where(in_organization)
            .order_by(MobileSuitDB.name, MobileSuitDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(MobileSuitDB).where(in_organization)
        ).scalar_one()
        links = self._get_links(link_filters, [suit.id for suit in suits])
        return Page[OrganizationMobileSuitEntity](
            items=[
                OrganizationMobileSuitEntity.model_validate(
                    {
                        "links": links.get(suit.id, []),
                        "mobile_suit": MobileSuitCardEntity.model_validate(suit),
                    }
                )
                for suit in suits
            ],
            total=total,
        )

    def create_or_update(self, *, payload: Mapping[str, Any]) -> OrganizationEntity:
        """Upsert an organization on its slug (SQLA-25)."""
        organization = self._upsert(
            OrganizationDB, payload=payload, conflict_columns=["slug"]
        )
        return OrganizationEntity.model_validate(organization)

    def create_or_update_appearance(
        self, *, payload: Mapping[str, Any]
    ) -> OrganizationAppearanceEntity:
        """Upsert an organization's appearance in a work."""
        appearance = self._upsert(
            OrganizationAppearanceDB,
            payload=payload,
            conflict_columns=["organization_id", "work_id"],
        )
        return OrganizationAppearanceEntity.model_validate(appearance)

    def create_or_update_slug_redirect(
        self, *, payload: Mapping[str, Any]
    ) -> OrganizationSlugRedirectEntity:
        """Upsert an old slug, pointing it at an organization (D2)."""
        redirect = self._upsert(
            OrganizationSlugRedirectDB, payload=payload, conflict_columns=["old_slug"]
        )
        return OrganizationSlugRedirectEntity.model_validate(redirect)

    @classmethod
    def _organization_has_slug(cls, slug: str) -> ColumnElement[bool]:
        """Match the organization with this current or old slug (D2)."""
        return cls._has_slug(
            OrganizationDB.slug,
            OrganizationDB.id,
            OrganizationSlugRedirectDB.old_slug,
            OrganizationSlugRedirectDB.organization_id,
            slug,
        )

    def _get_appearances(self, organization_id: uuid.UUID) -> list[CitedWorkEntity]:
        """Return the organization's works, first released first."""
        appearances = self.db_session.scalars(
            select(OrganizationAppearanceDB)
            .join(OrganizationAppearanceDB.work)
            .options(
                contains_eager(OrganizationAppearanceDB.work).joinedload(
                    WorkDB.continuity
                ),
                joinedload(OrganizationAppearanceDB.source),
            )
            .where(OrganizationAppearanceDB.organization_id == organization_id)
            .order_by(WorkDB.start_date.asc().nulls_last(), WorkDB.title, WorkDB.slug)
        ).all()
        return [
            CitedWorkEntity.model_validate(
                {
                    "created_at": appearance.created_at,
                    "source": SourceCitationEntity.model_validate(appearance.source),
                    "work": WorkCardEntity.model_validate(appearance.work),
                }
            )
            for appearance in appearances
        ]

    def _get_links(
        self, link_filters: list[ColumnElement[bool]], suit_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[OrganizationLinkEntity]]:
        """Return the page's links, grouped by suit, in role order.

        Within a role, links with a work come first, earliest first;
        links with no recorded work come last. Skipped for an empty
        page.
        """
        if not suit_ids:
            return {}
        rows = self.db_session.execute(
            select(MobileSuitOrganizationDB, WorkDB)
            .outerjoin(WorkDB, WorkDB.id == MobileSuitOrganizationDB.work_id)
            .options(joinedload(MobileSuitOrganizationDB.source))
            .where(*link_filters, MobileSuitOrganizationDB.mobile_suit_id.in_(suit_ids))
            .order_by(
                MobileSuitOrganizationDB.role,
                MobileSuitOrganizationDB.work_id.is_(None),
                WorkDB.start_date.asc().nulls_last(),
                WorkDB.title,
                MobileSuitOrganizationDB.id,
            )
        ).all()
        grouped: dict[uuid.UUID, list[OrganizationLinkEntity]] = {}
        for link, work in rows:
            grouped.setdefault(link.mobile_suit_id, []).append(
                OrganizationLinkEntity.model_validate(
                    {
                        "created_at": link.created_at,
                        "role": link.role,
                        "source": SourceCitationEntity.model_validate(link.source),
                        "work": optional_work_ref(work),
                    }
                )
            )
        return grouped
