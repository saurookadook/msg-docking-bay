"""Data access for ``spec_sheet_powerplants`` (SQLA-16)."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select

from models.base.facade import BaseFacade
from models.powerplant.db import PowerplantDB
from models.powerplant.entity import PowerplantRefEntity
from models.spec_sheet_powerplant.db import SpecSheetPowerplantDB
from models.spec_sheet_powerplant.entity import PowerplantListingEntity


class SpecSheetPowerplantFacade(BaseFacade):
    """Read which powerplants each spec sheet lists."""

    def get_for_sheets(
        self, spec_sheet_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[PowerplantListingEntity]]:
        """Return each sheet's powerplants, in one statement.

        Ordered by name. A sheet lists each powerplant once, so the
        powerplant's slug is a unique last key (RDB-22). Every sheet
        given has a key, empty when it lists none. No sheets send no
        statement, so a suit without sheets costs nothing here.
        """
        by_sheet: dict[uuid.UUID, list[PowerplantListingEntity]] = {
            sheet_id: [] for sheet_id in spec_sheet_ids
        }
        if not by_sheet:
            return by_sheet
        rows = self.db_session.execute(
            select(SpecSheetPowerplantDB, PowerplantDB)
            .join(PowerplantDB, PowerplantDB.id == SpecSheetPowerplantDB.powerplant_id)
            .where(SpecSheetPowerplantDB.spec_sheet_id.in_(list(by_sheet)))
            .order_by(PowerplantDB.name, PowerplantDB.slug)
        ).all()
        for listing, powerplant in rows:
            by_sheet[listing.spec_sheet_id].append(
                PowerplantListingEntity.model_validate(
                    {
                        "created_at": listing.created_at,
                        "powerplant": PowerplantRefEntity.model_validate(powerplant),
                        "note": listing.note,
                        "quantity_max": listing.quantity_max,
                        "quantity_min": listing.quantity_min,
                    }
                )
            )
        return by_sheet
