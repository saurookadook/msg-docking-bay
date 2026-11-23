"""Data access for ``organizations`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any, Final

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import contains_eager, joinedload

from constants.catalog import MobileSuitOrganizationRole
from models.base.facade import BaseFacade, SlugColumns, normalize_search
from models.base.page import Page
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import (
    MobileSuitCardEntity,
    OrganizationMobileSuitEntity,
)
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_organization.facade import MobileSuitOrganizationFacade
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

_SLUG_COLUMNS: Final = SlugColumns(
    OrganizationDB.slug,
    OrganizationDB.id,
    OrganizationSlugRedirectDB.old_slug,
    OrganizationSlugRedirectDB.organization_id,
)


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

        ``q`` matches the normalized slug and name, prefix matches
        first (D8).
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
            columns = (OrganizationDB.slug, OrganizationDB.name)
            filters.append(self._search_filter(columns, needle))
            order.append(self._prefix_rank(columns, needle))

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
        return self._first_by_slug(
            select(OrganizationDB.id),
            slug,
            columns=_SLUG_COLUMNS,
            not_found=OrganizationFacade.NotFoundError,
            record="Organization",
        )

    def get_one_by_slug(self, slug: str) -> OrganizationDetailEntity:
        """Return an organization with its parent, units and works.

        An old slug finds the renamed organization (D2). Three
        statements, however many rows the lists hold (PYTEST-24).

        Raises:
            OrganizationFacade.NotFoundError: when no slug matches.
        """
        organization = self._first_by_slug(
            select(OrganizationDB).options(
                joinedload(OrganizationDB.parent_organization)
            ),
            slug,
            columns=_SLUG_COLUMNS,
            not_found=OrganizationFacade.NotFoundError,
            record="Organization",
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
        links = MobileSuitOrganizationFacade(
            db_session=self.db_session
        ).get_links_for_suits([suit.id for suit in suits], link_filters=link_filters)
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
        return self._upsert_slug_redirect(
            OrganizationSlugRedirectDB, OrganizationSlugRedirectEntity, payload=payload
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
