"""Data access for ``mobile_suits`` (SQLA-16)."""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any, Final

from sqlalchemy import ColumnElement, case, func, or_, select
from sqlalchemy.orm import aliased, contains_eager, joinedload

from constants.catalog import UnitType
from models.base.entity import BaseEntityModel
from models.base.facade import BaseFacade, SlugColumns, normalize_search
from models.base.page import Page
from models.continuity.db import ContinuityDB
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import (
    MobileSuitAppearanceCardEntity,
    MobileSuitCardEntity,
    MobileSuitDetailEntity,
    MobileSuitEntity,
    RelatedMobileSuitEntity,
    WorkAppearanceEntity,
)
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.mobile_suit_appearance.entity import MobileSuitAppearanceEntity
from models.mobile_suit_designer.facade import MobileSuitDesignerFacade
from models.mobile_suit_organization.facade import MobileSuitOrganizationFacade
from models.mobile_suit_pilot.facade import MobileSuitPilotFacade
from models.mobile_suit_relation.db import MobileSuitRelationDB
from models.mobile_suit_relation.entity import MobileSuitRelationEntity
from models.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDB
from models.mobile_suit_slug_redirect.entity import MobileSuitSlugRedirectEntity
from models.source.db import SourceDB
from models.source.entity import SourceCitationEntity
from models.spec_sheet.db import SpecSheetDB
from models.spec_sheet.entity import (
    SPEC_SHEET_FIELDS,
    SPEC_SHEET_PART_KINDS,
    MobileSuitSpecSheetEntity,
    SpecSheetEntity,
    SpecSheetField,
    SpecSheetPartKind,
)
from models.spec_sheet_armament.facade import SpecSheetArmamentFacade
from models.spec_sheet_equipment.facade import SpecSheetEquipmentFacade
from models.spec_sheet_material.facade import SpecSheetMaterialFacade
from models.spec_sheet_powerplant.facade import SpecSheetPowerplantFacade
from models.work.db import WorkDB
from models.work.entity import WorkCardEntity
from models.work.facade import WorkFacade

type SheetParts = Mapping[
    SpecSheetPartKind, Mapping[uuid.UUID, Sequence[BaseEntityModel]]
]
"""Each kind's listings by sheet id, from ``get_for_sheets``."""

_PART_FACADES: Final[
    Mapping[
        SpecSheetPartKind,
        type[
            SpecSheetArmamentFacade
            | SpecSheetEquipmentFacade
            | SpecSheetMaterialFacade
            | SpecSheetPowerplantFacade
        ],
    ]
] = {
    "armaments": SpecSheetArmamentFacade,
    "equipment": SpecSheetEquipmentFacade,
    "materials": SpecSheetMaterialFacade,
    "powerplants": SpecSheetPowerplantFacade,
}
"""The junction facade that reads each part kind."""


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
        the current one (D2). Eleven statements, however many rows each
        list holds: the suit, one per list, and one per part kind for
        every sheet at once. A suit with no sheets skips the part kinds
        and costs seven (PYTEST-24).

        Raises:
            MobileSuitFacade.NotFoundError: when no suit has the slug.
        """
        suit = self._first_by_slug(
            select(MobileSuitDB).options(joinedload(MobileSuitDB.continuity)),
            slug,
            columns=SlugColumns(
                MobileSuitDB.slug,
                MobileSuitDB.id,
                MobileSuitSlugRedirectDB.old_slug,
                MobileSuitSlugRedirectDB.mobile_suit_id,
            ),
            not_found=MobileSuitFacade.NotFoundError,
            record="Mobile suit",
        )
        return MobileSuitDetailEntity.model_validate(
            {
                **MobileSuitCardEntity.model_validate(suit).model_dump(),
                "appearances": self._get_appearances(suit.id),
                "designers": MobileSuitDesignerFacade(
                    db_session=self.db_session
                ).get_for_suit(suit.id),
                "organizations": MobileSuitOrganizationFacade(
                    db_session=self.db_session
                ).get_for_suit(suit.id),
                "pilots": MobileSuitPilotFacade(
                    db_session=self.db_session
                ).get_for_suit(suit.id),
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
        return self._upsert_slug_redirect(
            MobileSuitSlugRedirectDB, MobileSuitSlugRedirectEntity, payload=payload
        )

    def _get_spec_sheets(
        self, mobile_suit_id: uuid.UUID
    ) -> list[MobileSuitSpecSheetEntity]:
        """Return the suit's sheets, base sheets first, gaps filled.

        Then by configuration, then by source. A named sheet takes each
        missing value from the same source's base sheet, and lists the
        columns it took in ``inherited_fields``; likewise each empty
        part list, in ``inherited_parts``. One statement for the sheets,
        then one per part kind for all of them.
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
        sheet_ids = [sheet.id for sheet in sheets]
        parts: SheetParts = {
            kind: _PART_FACADES[kind](db_session=self.db_session).get_for_sheets(
                sheet_ids
            )
            for kind in SPEC_SHEET_PART_KINDS
        }
        base_by_source = {
            sheet.source_id: sheet for sheet in sheets if sheet.configuration is None
        }
        return [
            _filled_sheet(sheet, base_by_source.get(sheet.source_id), parts)
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


def _filled_sheet(
    sheet: SpecSheetDB, base: SpecSheetDB | None, parts: SheetParts
) -> MobileSuitSpecSheetEntity:
    """Serve a sheet, filling a named one's gaps from its base sheet.

    A gap is a null measurement or an empty part list; the base sheet
    fills it only where the base has a value or a listing.
    """
    values: dict[str, float | None] = {
        field: getattr(sheet, field) for field in SPEC_SHEET_FIELDS
    }
    part_lists: dict[SpecSheetPartKind, Sequence[BaseEntityModel]] = {
        kind: parts[kind][sheet.id] for kind in SPEC_SHEET_PART_KINDS
    }
    inherited: Sequence[SpecSheetField] = []
    inherited_parts: list[SpecSheetPartKind] = []
    if sheet.configuration is not None and base is not None:
        inherited = [
            field
            for field in SPEC_SHEET_FIELDS
            if values[field] is None and getattr(base, field) is not None
        ]
        values |= {field: getattr(base, field) for field in inherited}
        inherited_parts = [
            kind
            for kind in SPEC_SHEET_PART_KINDS
            if not part_lists[kind] and parts[kind][base.id]
        ]
        part_lists |= {kind: parts[kind][base.id] for kind in inherited_parts}
    return MobileSuitSpecSheetEntity.model_validate(
        {
            **values,
            **part_lists,
            "configuration": sheet.configuration,
            "created_at": sheet.created_at,
            "inherited_fields": list(inherited),
            "inherited_parts": inherited_parts,
            "source": SourceCitationEntity.model_validate(sheet.source),
            "updated_at": sheet.updated_at,
        }
    )
