"""Data access for ``mobile_suits`` (SQLA-16)."""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import ColumnElement, case, func, or_, select
from sqlalchemy.orm import aliased, contains_eager, joinedload

from constants.catalog import UnitType
from models.base.facade import BaseFacade, normalize_search
from models.base.page import Page
from models.character.db import CharacterDB
from models.character.entity import CharacterRefEntity
from models.continuity.db import ContinuityDB
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mechanical_designer.entity import MechanicalDesignerRefEntity
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import (
    DesignerCreditEntity,
    MobileSuitAppearanceCardEntity,
    MobileSuitCardEntity,
    MobileSuitDetailEntity,
    MobileSuitEntity,
    OrganizationCreditEntity,
    PilotCreditEntity,
    RelatedMobileSuitEntity,
    WorkAppearanceEntity,
)
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.mobile_suit_appearance.entity import MobileSuitAppearanceEntity
from models.mobile_suit_designer.db import MobileSuitDesignerDB
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.mobile_suit_relation.db import MobileSuitRelationDB
from models.mobile_suit_relation.entity import MobileSuitRelationEntity
from models.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDB
from models.mobile_suit_slug_redirect.entity import MobileSuitSlugRedirectEntity
from models.organization.db import OrganizationDB
from models.organization.entity import OrganizationRefEntity
from models.source.db import SourceDB
from models.source.entity import SourceCitationEntity
from models.spec_sheet.db import SpecSheetDB
from models.spec_sheet.entity import (
    SPEC_SHEET_FIELDS,
    MobileSuitSpecSheetEntity,
    SpecSheetEntity,
    SpecSheetField,
)
from models.work.db import WorkDB
from models.work.entity import WorkCardEntity
from models.work.facade import WorkFacade, optional_work_ref


class MobileSuitFacade(BaseFacade):
    """Read and write mobile suits and the rows that hang off them."""

    class NotFoundError(Exception):
        """No suit has the slug, as a current or an old one."""

    def get_page(
        self,
        *,
        continuity_slug: str | None = None,
        work_slug: str | None = None,
        unit_type: UnitType | None = None,
        q: str | None = None,
        limit: int,
        offset: int,
    ) -> Page[MobileSuitCardEntity]:
        """Return one page of suits, by name (D3).

        ``q`` matches the slug and model number after normalization
        (D8), and ranks prefix matches first; a ``q`` with nothing left
        after normalization is no filter. Filters match current slugs
        only: an unknown continuity or work gives an empty page.
        """
        filters: list[ColumnElement[bool]] = []
        if continuity_slug is not None:
            filters.append(
                MobileSuitDB.continuity_id.in_(
                    select(ContinuityDB.id).where(ContinuityDB.slug == continuity_slug)
                )
            )
        if work_slug is not None:
            filters.append(
                MobileSuitDB.id.in_(
                    select(MobileSuitAppearanceDB.mobile_suit_id)
                    .join(WorkDB, WorkDB.id == MobileSuitAppearanceDB.work_id)
                    .where(WorkDB.slug == work_slug)
                )
            )
        if unit_type is not None:
            filters.append(MobileSuitDB.unit_type == unit_type)
        order: list[ColumnElement[Any]] = []
        needle = normalize_search(q)
        if needle is not None:
            columns = (MobileSuitDB.slug, MobileSuitDB.model_number)
            filters.append(self._search_filter(columns, needle))
            order.append(self._prefix_rank(columns, needle))

        suits = self.db_session.scalars(
            select(MobileSuitDB)
            .options(joinedload(MobileSuitDB.continuity))
            .where(*filters)
            .order_by(*order, MobileSuitDB.name, MobileSuitDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(MobileSuitDB).where(*filters)
        ).scalar_one()
        return Page[MobileSuitCardEntity](
            items=[MobileSuitCardEntity.model_validate(suit) for suit in suits],
            total=total,
        )

    def get_page_by_work_slug(
        self, work_slug: str, *, limit: int, offset: int
    ) -> Page[MobileSuitAppearanceCardEntity]:
        """Return one page of the suits in a work, debuts first.

        The work is found by any of its slugs (D2); the suits after the
        debuts are by name.

        Raises:
            WorkFacade.NotFoundError: when no work has the slug.
        """
        work_id = WorkFacade(db_session=self.db_session).get_id_by_slug(work_slug)
        in_work = MobileSuitAppearanceDB.work_id == work_id

        rows = self.db_session.execute(
            select(MobileSuitAppearanceDB, MobileSuitDB)
            .join(
                MobileSuitDB, MobileSuitDB.id == MobileSuitAppearanceDB.mobile_suit_id
            )
            .options(joinedload(MobileSuitDB.continuity))
            .where(in_work)
            .order_by(
                MobileSuitAppearanceDB.is_debut.desc(),
                MobileSuitDB.name,
                MobileSuitDB.id,
            )
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(MobileSuitAppearanceDB).where(in_work)
        ).scalar_one()
        return Page[MobileSuitAppearanceCardEntity](
            items=[
                MobileSuitAppearanceCardEntity.model_validate(
                    {
                        **MobileSuitCardEntity.model_validate(suit).model_dump(),
                        "first_episode": appearance.first_episode,
                        "is_debut": appearance.is_debut,
                        "last_episode": appearance.last_episode,
                    }
                )
                for appearance, suit in rows
            ],
            total=total,
        )

    def get_one_by_slug(self, slug: str) -> MobileSuitDetailEntity:
        """Return a suit with its sheets, relations, works and credits.

        An old slug finds the renamed suit, whose ``slug`` then holds
        the current one (D2). Seven statements, however many rows each
        list holds: the suit, then one per list (PYTEST-24).

        Raises:
            MobileSuitFacade.NotFoundError: when no suit has the slug.
        """
        suit = self.db_session.scalars(
            select(MobileSuitDB)
            .options(joinedload(MobileSuitDB.continuity))
            .where(
                self._has_slug(
                    MobileSuitDB.slug,
                    MobileSuitDB.id,
                    MobileSuitSlugRedirectDB.old_slug,
                    MobileSuitSlugRedirectDB.mobile_suit_id,
                    slug,
                )
            )
            .order_by(self._current_slug_first(MobileSuitDB.slug, slug))
            .limit(1)
        ).first()
        if suit is None:
            raise MobileSuitFacade.NotFoundError(
                f"Mobile suit record with ``slug='{slug}'`` not found"
            )

        return MobileSuitDetailEntity.model_validate(
            {
                **MobileSuitCardEntity.model_validate(suit).model_dump(),
                "appearances": self._get_appearances(suit.id),
                "designers": self._get_designers(suit.id),
                "organizations": self._get_organizations(suit.id),
                "pilots": self._get_pilots(suit.id),
                "relations": self._get_relations(suit.id),
                "spec_sheets": self._get_spec_sheets(suit.id),
            }
        )

    def create_or_update(self, *, payload: Mapping[str, Any]) -> MobileSuitEntity:
        """Upsert a suit on its slug (SQLA-25)."""
        suit = self._upsert(MobileSuitDB, payload=payload, conflict_columns=["slug"])
        return MobileSuitEntity.model_validate(suit)

    def create_or_update_spec_sheet(
        self, *, payload: Mapping[str, Any]
    ) -> SpecSheetEntity:
        """Upsert a spec sheet on its suit, source and configuration.

        A null ``configuration`` is the base sheet: the key treats nulls
        as equal, so each suit has one base sheet per source.
        """
        sheet = self._upsert(
            SpecSheetDB,
            payload=payload,
            conflict_columns=["mobile_suit_id", "source_id", "configuration"],
        )
        return SpecSheetEntity.model_validate(sheet)

    def create_or_update_relation(
        self, *, payload: Mapping[str, Any]
    ) -> MobileSuitRelationEntity:
        """Upsert a relation on its edge, updating only its source."""
        relation = self._upsert(
            MobileSuitRelationDB,
            payload=payload,
            conflict_columns=[
                "from_mobile_suit_id",
                "relation_type",
                "to_mobile_suit_id",
            ],
        )
        return MobileSuitRelationEntity.model_validate(relation)

    def create_or_update_appearance(
        self, *, payload: Mapping[str, Any]
    ) -> MobileSuitAppearanceEntity:
        """Upsert a suit's appearance in a work, on the pair."""
        appearance = self._upsert(
            MobileSuitAppearanceDB,
            payload=payload,
            conflict_columns=["mobile_suit_id", "work_id"],
        )
        return MobileSuitAppearanceEntity.model_validate(appearance)

    def create_or_update_slug_redirect(
        self, *, payload: Mapping[str, Any]
    ) -> MobileSuitSlugRedirectEntity:
        """Upsert an old slug, pointing it at a suit (D2)."""
        redirect = self._upsert(
            MobileSuitSlugRedirectDB, payload=payload, conflict_columns=["old_slug"]
        )
        return MobileSuitSlugRedirectEntity.model_validate(redirect)

    def _get_spec_sheets(
        self, mobile_suit_id: uuid.UUID
    ) -> list[MobileSuitSpecSheetEntity]:
        """Return the suit's sheets, base sheets first, gaps filled.

        Then by configuration, then by source. A named sheet takes each
        missing value from the same source's base sheet, and lists the
        columns it took in ``inherited_fields``.
        """
        sheets = self.db_session.scalars(
            select(SpecSheetDB)
            .join(SpecSheetDB.source)
            .options(contains_eager(SpecSheetDB.source))
            .where(SpecSheetDB.mobile_suit_id == mobile_suit_id)
            .order_by(
                SpecSheetDB.configuration.asc().nulls_first(),
                SourceDB.kind,
                SourceDB.url,
                SpecSheetDB.id,
            )
        ).all()
        base_by_source = {
            sheet.source_id: sheet for sheet in sheets if sheet.configuration is None
        }
        return [
            _filled_sheet(sheet, base_by_source.get(sheet.source_id))
            for sheet in sheets
        ]

    def _get_relations(
        self, mobile_suit_id: uuid.UUID
    ) -> list[RelatedMobileSuitEntity]:
        """Return every edge that touches the suit, from its side (D5).

        Ordered by type, then direction, then the other suit's name.
        """
        other = aliased(MobileSuitDB)
        is_outgoing = MobileSuitRelationDB.from_mobile_suit_id == mobile_suit_id
        direction = case((is_outgoing, "outgoing"), else_="incoming").label("direction")
        other_id = case(
            (is_outgoing, MobileSuitRelationDB.to_mobile_suit_id),
            else_=MobileSuitRelationDB.from_mobile_suit_id,
        )
        rows = self.db_session.execute(
            select(MobileSuitRelationDB, other, direction)
            .join(other, other.id == other_id)
            .where(
                or_(
                    is_outgoing,
                    MobileSuitRelationDB.to_mobile_suit_id == mobile_suit_id,
                )
            )
            .options(
                joinedload(MobileSuitRelationDB.source), joinedload(other.continuity)
            )
            .order_by(
                MobileSuitRelationDB.relation_type, direction, other.name, other.slug
            )
        ).all()
        return [
            RelatedMobileSuitEntity.model_validate(
                {
                    "created_at": relation.created_at,
                    "direction": row_direction,
                    "mobile_suit": MobileSuitCardEntity.model_validate(other_suit),
                    "relation_type": relation.relation_type,
                    "source": SourceCitationEntity.model_validate(relation.source),
                }
            )
            for relation, other_suit, row_direction in rows
        ]

    def _get_appearances(self, mobile_suit_id: uuid.UUID) -> list[WorkAppearanceEntity]:
        """Return the works the suit is in, first released first."""
        appearances = self.db_session.scalars(
            select(MobileSuitAppearanceDB)
            .join(MobileSuitAppearanceDB.work)
            .options(
                contains_eager(MobileSuitAppearanceDB.work).joinedload(
                    WorkDB.continuity
                ),
                joinedload(MobileSuitAppearanceDB.source),
            )
            .where(MobileSuitAppearanceDB.mobile_suit_id == mobile_suit_id)
            .order_by(WorkDB.start_date.asc().nulls_last(), WorkDB.title, WorkDB.slug)
        ).all()
        return [
            WorkAppearanceEntity.model_validate(
                {
                    "created_at": appearance.created_at,
                    "first_episode": appearance.first_episode,
                    "is_debut": appearance.is_debut,
                    "last_episode": appearance.last_episode,
                    "source": SourceCitationEntity.model_validate(appearance.source),
                    "work": WorkCardEntity.model_validate(appearance.work),
                }
            )
            for appearance in appearances
        ]

    def _get_designers(self, mobile_suit_id: uuid.UUID) -> list[DesignerCreditEntity]:
        """Return the suit's designers, by name."""
        rows = self.db_session.execute(
            select(MobileSuitDesignerDB, MechanicalDesignerDB)
            .join(
                MechanicalDesignerDB,
                MechanicalDesignerDB.id == MobileSuitDesignerDB.mechanical_designer_id,
            )
            .options(joinedload(MobileSuitDesignerDB.source))
            .where(MobileSuitDesignerDB.mobile_suit_id == mobile_suit_id)
            .order_by(MechanicalDesignerDB.name, MechanicalDesignerDB.slug)
        ).all()
        return [
            DesignerCreditEntity.model_validate(
                {
                    "created_at": credit.created_at,
                    "mechanical_designer": MechanicalDesignerRefEntity.model_validate(
                        designer
                    ),
                    "source": SourceCitationEntity.model_validate(credit.source),
                }
            )
            for credit, designer in rows
        ]

    def _get_organizations(
        self, mobile_suit_id: uuid.UUID
    ) -> list[OrganizationCreditEntity]:
        """Return the suit's organizations, by role, work, then name.

        Links with no recorded work come after a role's other links.
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
                MobileSuitOrganizationDB.work_id.is_(None),
                WorkDB.start_date.asc().nulls_last(),
                WorkDB.title,
                OrganizationDB.name,
                OrganizationDB.slug,
            )
        ).all()
        return [
            OrganizationCreditEntity.model_validate(
                {
                    "created_at": link.created_at,
                    "organization": OrganizationRefEntity.model_validate(organization),
                    "role": link.role,
                    "source": SourceCitationEntity.model_validate(link.source),
                    "work": optional_work_ref(work),
                }
            )
            for link, organization, work in rows
        ]

    def _get_pilots(self, mobile_suit_id: uuid.UUID) -> list[PilotCreditEntity]:
        """Return the suit's pilots, by work, then by name.

        Pairings with no recorded work come after the ones with a work.
        """
        rows = self.db_session.execute(
            select(MobileSuitPilotDB, CharacterDB, WorkDB)
            .join(CharacterDB, CharacterDB.id == MobileSuitPilotDB.character_id)
            .outerjoin(WorkDB, WorkDB.id == MobileSuitPilotDB.work_id)
            .options(joinedload(MobileSuitPilotDB.source))
            .where(MobileSuitPilotDB.mobile_suit_id == mobile_suit_id)
            .order_by(
                MobileSuitPilotDB.work_id.is_(None),
                WorkDB.start_date.asc().nulls_last(),
                WorkDB.title,
                CharacterDB.name,
                CharacterDB.slug,
            )
        ).all()
        return [
            PilotCreditEntity.model_validate(
                {
                    "character": CharacterRefEntity.model_validate(character),
                    "created_at": pilot.created_at,
                    "source": SourceCitationEntity.model_validate(pilot.source),
                    "work": optional_work_ref(work),
                }
            )
            for pilot, character, work in rows
        ]


def _filled_sheet(
    sheet: SpecSheetDB, base: SpecSheetDB | None
) -> MobileSuitSpecSheetEntity:
    """Serve a sheet, filling a named one's gaps from its base sheet."""
    values: dict[str, float | None] = {
        field: getattr(sheet, field) for field in SPEC_SHEET_FIELDS
    }
    inherited: Sequence[SpecSheetField] = []
    if sheet.configuration is not None and base is not None:
        inherited = [
            field
            for field in SPEC_SHEET_FIELDS
            if values[field] is None and getattr(base, field) is not None
        ]
        values |= {field: getattr(base, field) for field in inherited}
    return MobileSuitSpecSheetEntity.model_validate(
        {
            **values,
            "configuration": sheet.configuration,
            "created_at": sheet.created_at,
            "inherited_fields": list(inherited),
            "source": SourceCitationEntity.model_validate(sheet.source),
            "updated_at": sheet.updated_at,
        }
    )
