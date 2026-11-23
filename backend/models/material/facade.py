"""Data access for ``materials`` (SQLA-16)."""

from collections.abc import Mapping
from typing import Any

from models.base.facade import BaseFacade
from models.material.db import MaterialDB
from models.material.entity import MaterialEntity


class MaterialFacade(BaseFacade):
    """Write materials; sheets read them through their listings."""

    def create_or_update(self, *, payload: Mapping[str, Any]) -> MaterialEntity:
        """Upsert a material on its slug (SQLA-25)."""
        part = self._upsert(MaterialDB, payload=payload, conflict_columns=["slug"])
        return MaterialEntity.model_validate(part)
