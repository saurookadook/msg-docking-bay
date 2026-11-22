"""Data access for ``spec_sheet_equipment`` (SQLA-16)."""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import select

from models.base.facade import BaseFacade
from models.equipment.db import EquipmentDB
from models.equipment.entity import EquipmentRefEntity
from models.spec_sheet_equipment.db import SpecSheetEquipmentDB
from models.spec_sheet_equipment.entity import (
    EquipmentListingEntity,
    SpecSheetEquipmentEntity,
)


class SpecSheetEquipmentFacade(BaseFacade):
    """Read and write which equipment each spec sheet lists."""

    def get_for_sheets(
        self, spec_sheet_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[EquipmentListingEntity]]:
        """Return each sheet's equipment, in one statement.

        Ordered by fit, standard before optional, then by name. A sheet
        lists each item once per fit, so the item's slug is a unique
        last key (RDB-22). Every sheet given has a key, empty when it
        lists none. No sheets send no statement, so a suit without
        sheets costs nothing here.
        """
        by_sheet: dict[uuid.UUID, list[EquipmentListingEntity]] = {
            sheet_id: [] for sheet_id in spec_sheet_ids
        }
        if not by_sheet:
            return by_sheet
        rows = self.db_session.execute(
            select(SpecSheetEquipmentDB, EquipmentDB)
            .join(EquipmentDB, EquipmentDB.id == SpecSheetEquipmentDB.equipment_id)
            .where(SpecSheetEquipmentDB.spec_sheet_id.in_(list(by_sheet)))
            .order_by(SpecSheetEquipmentDB.fit, EquipmentDB.name, EquipmentDB.slug)
        ).all()
        for listing, equipment in rows:
            by_sheet[listing.spec_sheet_id].append(
                EquipmentListingEntity.model_validate(
                    {
                        "created_at": listing.created_at,
                        "fit": listing.fit,
                        "equipment": EquipmentRefEntity.model_validate(equipment),
                        "note": listing.note,
                    }
                )
            )
        return by_sheet

    def create_or_update(
        self, *, payload: Mapping[str, Any]
    ) -> SpecSheetEquipmentEntity:
        """Upsert a listing on its equipment, fit and spec sheet."""
        listing = self._upsert(
            SpecSheetEquipmentDB,
            payload=payload,
            conflict_columns=["equipment_id", "fit", "spec_sheet_id"],
        )
        return SpecSheetEquipmentEntity.model_validate(listing)
