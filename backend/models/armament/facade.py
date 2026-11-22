"""Data access for ``armaments`` (SQLA-16)."""

from collections.abc import Mapping
from typing import Any

from models.armament.db import ArmamentDB
from models.armament.entity import ArmamentEntity
from models.base.facade import BaseFacade


class ArmamentFacade(BaseFacade):
    """Write armaments; sheets read them through their listings."""

    def create_or_update(self, *, payload: Mapping[str, Any]) -> ArmamentEntity:
        """Upsert an armament on its slug (SQLA-25)."""
        part = self._upsert(ArmamentDB, payload=payload, conflict_columns=["slug"])
        return ArmamentEntity.model_validate(part)
