"""Data access for ``mobile_suit_organizations`` (SQLA-16).

The suit detail lists a suit's organizations and the organization's
suit page lists its links; both read through here, so the table's
ordering and row shape live in one place.
"""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import ColumnElement, select
from sqlalchemy.orm import joinedload

from models.base.facade import BaseFacade
from models.mobile_suit.entity import OrganizationCreditEntity, OrganizationLinkEntity
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_organization.entity import MobileSuitOrganizationEntity
from models.organization.db import OrganizationDB
from models.organization.entity import OrganizationRefEntity
from models.source.entity import SourceCitationEntity
from models.work.db import WorkDB
from models.work.entity import WorkRefEntity
from models.work.facade import WorkFacade


class MobileSuitOrganizationFacade(BaseFacade):
    """Read and write organizations' roles for suits, by work."""

    def get_for_suit(self, mobile_suit_id: uuid.UUID) -> list[OrganizationCreditEntity]:
        """Return a suit's organizations, by role, work, then name.

        Links with no recorded work come after a role's other links.
        One statement; an unknown suit has no organizations.
        """
        rows = self.db_session.execute(
            select(MobileSuitOrganizationDB, OrganizationDB, WorkDB)
            .join(
                OrganizationDB,
                OrganizationDB.id == MobileSuitOrganizationDB.organization_id,
            )
            .outerjoin(WorkDB, WorkDB.id == MobileSuitOrganizationDB.work_id)
            .options(joinedload(MobileSuitOrganizationDB.source))
            .where(MobileSuitOrganizationDB.mobile_suit_id == mobile_suit_id)
            .order_by(
                MobileSuitOrganizationDB.role,
                *WorkFacade.released_first(MobileSuitOrganizationDB.work_id),
                OrganizationDB.name,
                OrganizationDB.slug,
                MobileSuitOrganizationDB.id,
            )
        ).all()
        return [
            OrganizationCreditEntity.model_validate(
                {
                    "created_at": link.created_at,
                    "organization": OrganizationRefEntity.model_validate(organization),
                    "role": link.role,
                    "source": SourceCitationEntity.model_validate(link.source),
                    "work": WorkRefEntity.from_optional(work),
                }
            )
            for link, organization, work in rows
        ]

    def get_links_for_suits(
        self,
        suit_ids: Sequence[uuid.UUID],
        *,
        link_filters: Sequence[ColumnElement[bool]],
    ) -> dict[uuid.UUID, list[OrganizationLinkEntity]]:
        """Return the links of a page of suits, grouped by suit.

        In role order; within a role, links with a work come first,
        earliest first. ``link_filters`` narrows the links the way the
        page was narrowed (an organization, a role). One statement, or
        none for an empty page.
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
                *WorkFacade.released_first(MobileSuitOrganizationDB.work_id),
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
                        "work": WorkRefEntity.from_optional(work),
                    }
                )
            )
        return grouped

    def create_or_update(
        self, *, payload: Mapping[str, Any]
    ) -> MobileSuitOrganizationEntity:
        """Upsert an organization link on its suit, role and work.

        As with pilots, the key treats a null ``work_id`` as one value.
        """
        link = self._upsert(
            MobileSuitOrganizationDB,
            payload=payload,
            conflict_columns=["mobile_suit_id", "organization_id", "role", "work_id"],
        )
        return MobileSuitOrganizationEntity.model_validate(link)
