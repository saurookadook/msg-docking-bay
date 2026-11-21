"""Data access for ``continuities`` (SQLA-16)."""

from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.base.facade import BaseFacade
from models.continuity.db import ContinuityDB
from models.continuity.entity import ContinuityCardEntity, ContinuityEntity


class ContinuityFacade(BaseFacade):
    """Read and write continuities."""

    def get_all(self) -> list[ContinuityCardEntity]:
        """Return every continuity, by name, each with its parent.

        Unpaginated: there are a few dozen timelines at most.
        """
        continuities = self.db_session.scalars(
            select(ContinuityDB)
            .options(joinedload(ContinuityDB.parent_continuity))
            .order_by(ContinuityDB.name, ContinuityDB.id)
        ).all()
        return [ContinuityCardEntity.model_validate(row) for row in continuities]

    def create_or_update(self, *, payload: Mapping[str, Any]) -> ContinuityEntity:
        """Upsert a continuity on its slug (SQLA-25)."""
        continuity = self._upsert(
            ContinuityDB, payload=payload, conflict_columns=["slug"]
        )
        return ContinuityEntity.model_validate(continuity)
