"""Data access for ``mobile_suit_designers`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.base.facade import BaseFacade
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mechanical_designer.entity import MechanicalDesignerRefEntity
from models.mobile_suit.entity import DesignerCreditEntity
from models.mobile_suit_designer.db import MobileSuitDesignerDB
from models.mobile_suit_designer.entity import MobileSuitDesignerEntity
from models.source.entity import SourceCitationEntity


class MobileSuitDesignerFacade(BaseFacade):
    """Read and write which designers are credited with which suits."""

    def get_for_suit(self, mobile_suit_id: uuid.UUID) -> list[DesignerCreditEntity]:
        """Return a suit's designers, by name.

        A suit credits each designer once, so the designer's slug is a
        unique last key (RDB-22). One statement; an unknown suit has no
        designers.
        """
        rows = self.db_session.execute(
            select(MobileSuitDesignerDB, MechanicalDesignerDB)
            .join(
                MechanicalDesignerDB,
                MechanicalDesignerDB.id == MobileSuitDesignerDB.mechanical_designer_id,
            )
            .options(joinedload(MobileSuitDesignerDB.source))
            .where(MobileSuitDesignerDB.mobile_suit_id == mobile_suit_id)
            .order_by(MechanicalDesignerDB.name, MechanicalDesignerDB.slug)
        ).all()
        return [
            DesignerCreditEntity.model_validate(
                {
                    "created_at": credit.created_at,
                    "mechanical_designer": MechanicalDesignerRefEntity.model_validate(
                        designer
                    ),
                    "source": SourceCitationEntity.model_validate(credit.source),
                }
            )
            for credit, designer in rows
        ]

    def create_or_update(
        self, *, payload: Mapping[str, Any]
    ) -> MobileSuitDesignerEntity:
        """Upsert a design credit on its designer and suit."""
        credit = self._upsert(
            MobileSuitDesignerDB,
            payload=payload,
            conflict_columns=["mechanical_designer_id", "mobile_suit_id"],
        )
        return MobileSuitDesignerEntity.model_validate(credit)
