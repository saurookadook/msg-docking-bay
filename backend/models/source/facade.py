"""Data access for ``sources`` (SQLA-16)."""

from collections.abc import Mapping
from typing import Any

from models.base.facade import BaseFacade
from models.source.db import SourceDB
from models.source.entity import SourceEntity


class SourceFacade(BaseFacade):
    """Write the pages that facts cite."""

    def create_or_update(self, *, payload: Mapping[str, Any]) -> SourceEntity:
        """Upsert a source on ``(kind, external_id)``.

        Re-ingesting a page updates its row in place (ADR 0002). An
        unchanged row keeps its ``updated_at`` (SQLA-25).
        """
        source = self._upsert(
            SourceDB, payload=payload, conflict_columns=["kind", "external_id"]
        )
        return SourceEntity.model_validate(source)
