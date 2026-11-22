"""Data access for ``equipment`` (SQLA-16)."""

from collections.abc import Mapping
from typing import Any

from models.base.facade import BaseFacade
from models.equipment.db import EquipmentDB
from models.equipment.entity import EquipmentEntity


class EquipmentFacade(BaseFacade):
    """Write equipment; sheets read them through their listings."""

    def create_or_update(self, *, payload: Mapping[str, Any]) -> EquipmentEntity:
        """Upsert an item of equipment on its slug (SQLA-25)."""
        part = self._upsert(EquipmentDB, payload=payload, conflict_columns=["slug"])
        return EquipmentEntity.model_validate(part)
