"""Data access for ``spec_sheet_armaments`` (SQLA-16)."""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import select

from models.armament.db import ArmamentDB
from models.armament.entity import ArmamentRefEntity
from models.base.facade import BaseFacade
from models.spec_sheet_armament.db import SpecSheetArmamentDB
from models.spec_sheet_armament.entity import (
    ArmamentListingEntity,
    SpecSheetArmamentEntity,
)


class SpecSheetArmamentFacade(BaseFacade):
    """Read and write which armaments each spec sheet lists."""

    def get_for_sheets(
        self, spec_sheet_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[ArmamentListingEntity]]:
        """Return each sheet's armaments, in one statement.

        Ordered by mount, in its declared order (fixed, handheld, then
        the optional ones), then by name. A sheet lists each weapon once
        per mount, so the weapon's slug is a unique last key (RDB-22).
        Every sheet given has a key, empty when it lists none. No sheets
        send no statement, so a suit without sheets costs nothing here.
        """
        by_sheet: dict[uuid.UUID, list[ArmamentListingEntity]] = {
            sheet_id: [] for sheet_id in spec_sheet_ids
        }
        if not by_sheet:
            return by_sheet
        rows = self.db_session.execute(
            select(SpecSheetArmamentDB, ArmamentDB)
            .join(ArmamentDB, ArmamentDB.id == SpecSheetArmamentDB.armament_id)
            .where(SpecSheetArmamentDB.spec_sheet_id.in_(list(by_sheet)))
            .order_by(SpecSheetArmamentDB.mount, ArmamentDB.name, ArmamentDB.slug)
        ).all()
        for listing, armament in rows:
            by_sheet[listing.spec_sheet_id].append(
                ArmamentListingEntity.model_validate(
                    {
                        "created_at": listing.created_at,
                        "mount": listing.mount,
                        "armament": ArmamentRefEntity.model_validate(armament),
                        "note": listing.note,
                        "quantity_max": listing.quantity_max,
                        "quantity_min": listing.quantity_min,
                    }
                )
            )
        return by_sheet

    def create_or_update(
        self, *, payload: Mapping[str, Any]
    ) -> SpecSheetArmamentEntity:
        """Upsert a listing on its armament, mount and spec sheet."""
        listing = self._upsert(
            SpecSheetArmamentDB,
            payload=payload,
            conflict_columns=["armament_id", "mount", "spec_sheet_id"],
        )
        return SpecSheetArmamentEntity.model_validate(listing)
