"""Data access for ``powerplants`` (SQLA-16)."""

from collections.abc import Mapping
from typing import Any

from models.base.facade import BaseFacade
from models.powerplant.db import PowerplantDB
from models.powerplant.entity import PowerplantEntity


class PowerplantFacade(BaseFacade):
    """Write powerplants; sheets read them through their listings."""

    def create_or_update(self, *, payload: Mapping[str, Any]) -> PowerplantEntity:
        """Upsert a powerplant on its slug (SQLA-25)."""
        part = self._upsert(PowerplantDB, payload=payload, conflict_columns=["slug"])
        return PowerplantEntity.model_validate(part)
