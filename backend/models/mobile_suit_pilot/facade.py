"""Data access for ``mobile_suit_pilots`` (SQLA-16).

The suit detail lists a suit's pilots and the character detail lists a
character's suits; both read through here, so the table's ordering and
row shape live in one place.
"""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.base.facade import BaseFacade
from models.character.db import CharacterDB
from models.character.entity import CharacterRefEntity
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import (
    MobileSuitCardEntity,
    PilotCreditEntity,
    PilotedMobileSuitEntity,
)
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.mobile_suit_pilot.entity import MobileSuitPilotEntity
from models.source.entity import SourceCitationEntity
from models.work.db import WorkDB
from models.work.entity import WorkRefEntity
from models.work.facade import WorkFacade


class MobileSuitPilotFacade(BaseFacade):
    """Read and write who pilots which suit, and in which work."""

    def get_for_suit(self, mobile_suit_id: uuid.UUID) -> list[PilotCreditEntity]:
        """Return a suit's pilots, by work, then by name.

        Pairings with no recorded work come after the ones with a work.
        One statement; an unknown suit has no pilots.
        """
        rows = self.db_session.execute(
            select(MobileSuitPilotDB, CharacterDB, WorkDB)
            .join(CharacterDB, CharacterDB.id == MobileSuitPilotDB.character_id)
            .outerjoin(WorkDB, WorkDB.id == MobileSuitPilotDB.work_id)
            .options(joinedload(MobileSuitPilotDB.source))
            .where(MobileSuitPilotDB.mobile_suit_id == mobile_suit_id)
            .order_by(
                *WorkFacade.released_first(MobileSuitPilotDB.work_id),
                CharacterDB.name,
                CharacterDB.slug,
                MobileSuitPilotDB.id,
            )
        ).all()
        return [
            PilotCreditEntity.model_validate(
                {
                    "character": CharacterRefEntity.model_validate(character),
                    "created_at": pilot.created_at,
                    "source": SourceCitationEntity.model_validate(pilot.source),
                    "work": WorkRefEntity.from_optional(work),
                }
            )
            for pilot, character, work in rows
        ]

    def get_for_character(
        self, character_id: uuid.UUID
    ) -> list[PilotedMobileSuitEntity]:
        """Return the suits a character pilots, by work, then by name.

        Pairings with no recorded work come after the ones with a work.
        One statement; an unknown character pilots nothing.
        """
        rows = self.db_session.execute(
            select(MobileSuitPilotDB, MobileSuitDB, WorkDB)
            .join(MobileSuitDB, MobileSuitDB.id == MobileSuitPilotDB.mobile_suit_id)
            .outerjoin(WorkDB, WorkDB.id == MobileSuitPilotDB.work_id)
            .options(
                joinedload(MobileSuitPilotDB.source),
                joinedload(MobileSuitDB.continuity),
            )
            .where(MobileSuitPilotDB.character_id == character_id)
            .order_by(
                *WorkFacade.released_first(MobileSuitPilotDB.work_id),
                MobileSuitDB.name,
                MobileSuitDB.id,
                MobileSuitPilotDB.id,
            )
        ).all()
        return [
            PilotedMobileSuitEntity.model_validate(
                {
                    "created_at": pilot.created_at,
                    "mobile_suit": MobileSuitCardEntity.model_validate(suit),
                    "source": SourceCitationEntity.model_validate(pilot.source),
                    "work": WorkRefEntity.from_optional(work),
                }
            )
            for pilot, suit, work in rows
        ]

    def create_or_update(self, *, payload: Mapping[str, Any]) -> MobileSuitPilotEntity:
        """Upsert a pilot link on its character, suit and work.

        A null ``work_id`` is one pairing too: the key treats nulls as
        equal, so a rerun finds it.
        """
        pilot = self._upsert(
            MobileSuitPilotDB,
            payload=payload,
            conflict_columns=["character_id", "mobile_suit_id", "work_id"],
        )
        return MobileSuitPilotEntity.model_validate(pilot)
