"""Data access for ``spec_sheet_materials`` (SQLA-16)."""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import select

from models.base.facade import BaseFacade
from models.material.db import MaterialDB
from models.material.entity import MaterialRefEntity
from models.spec_sheet_material.db import SpecSheetMaterialDB
from models.spec_sheet_material.entity import (
    MaterialListingEntity,
    SpecSheetMaterialEntity,
)


class SpecSheetMaterialFacade(BaseFacade):
    """Read and write which materials each spec sheet lists."""

    def get_for_sheets(
        self, spec_sheet_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[MaterialListingEntity]]:
        """Return each sheet's materials, in one statement.

        Ordered by use, armor before frame, then by name. A sheet lists
        each material once per material use, so the material's slug is a
        unique last key (RDB-22). Every sheet given has a key, empty
        when it lists none. No sheets send no statement, so a suit
        without sheets costs nothing here.
        """
        by_sheet: dict[uuid.UUID, list[MaterialListingEntity]] = {
            sheet_id: [] for sheet_id in spec_sheet_ids
        }
        if not by_sheet:
            return by_sheet
        rows = self.db_session.execute(
            select(SpecSheetMaterialDB, MaterialDB)
            .join(MaterialDB, MaterialDB.id == SpecSheetMaterialDB.material_id)
            .where(SpecSheetMaterialDB.spec_sheet_id.in_(list(by_sheet)))
            .order_by(
                SpecSheetMaterialDB.material_use, MaterialDB.name, MaterialDB.slug
            )
        ).all()
        for listing, material in rows:
            by_sheet[listing.spec_sheet_id].append(
                MaterialListingEntity.model_validate(
                    {
                        "created_at": listing.created_at,
                        "material_use": listing.material_use,
                        "material": MaterialRefEntity.model_validate(material),
                        "note": listing.note,
                    }
                )
            )
        return by_sheet

    def create_or_update(
        self, *, payload: Mapping[str, Any]
    ) -> SpecSheetMaterialEntity:
        """Upsert a listing on its material, use and spec sheet."""
        listing = self._upsert(
            SpecSheetMaterialDB,
            payload=payload,
            conflict_columns=["material_id", "material_use", "spec_sheet_id"],
        )
        return SpecSheetMaterialEntity.model_validate(listing)
