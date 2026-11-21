"""Data access for ``characters`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import contains_eager, joinedload

from models.base.facade import BaseFacade, normalize_search
from models.base.page import Page
from models.character.db import CharacterDB
from models.character.detail import CharacterDetailEntity
from models.character.entity import CharacterCardEntity, CharacterEntity
from models.character_appearance.db import CharacterAppearanceDB
from models.character_appearance.entity import CharacterAppearanceEntity
from models.character_slug_redirect.db import CharacterSlugRedirectDB
from models.character_slug_redirect.entity import CharacterSlugRedirectEntity
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import MobileSuitCardEntity, PilotedMobileSuitEntity
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.source.entity import SourceCitationEntity
from models.work.db import WorkDB
from models.work.entity import CitedWorkEntity, WorkCardEntity
from models.work.facade import optional_work_ref


class CharacterFacade(BaseFacade):
    """Read and write characters, their appearances and old slugs."""

    class NotFoundError(Exception):
        """No character has the slug, as a current or an old one."""

    def get_page(
        self,
        *,
        work_slug: str | None = None,
        q: str | None = None,
        limit: int,
        offset: int,
    ) -> Page[CharacterCardEntity]:
        """Return one page of characters, by name (D3).

        ``q`` matches the normalized slug, prefix matches first (D8).
        ``work_slug`` matches current slugs only: an unknown work gives
        an empty page.
        """
        filters: list[ColumnElement[bool]] = []
        if work_slug is not None:
            filters.append(
                CharacterDB.id.in_(
                    select(CharacterAppearanceDB.character_id)
                    .join(WorkDB, WorkDB.id == CharacterAppearanceDB.work_id)
                    .where(WorkDB.slug == work_slug)
                )
            )
        order: list[ColumnElement[Any]] = []
        needle = normalize_search(q)
        if needle is not None:
            filters.append(self._search_filter((CharacterDB.slug,), needle))
            order.append(self._prefix_rank((CharacterDB.slug,), needle))

        characters = self.db_session.scalars(
            select(CharacterDB)
            .where(*filters)
            .order_by(*order, CharacterDB.name, CharacterDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(CharacterDB).where(*filters)
        ).scalar_one()
        return Page[CharacterCardEntity](
            items=[CharacterCardEntity.model_validate(row) for row in characters],
            total=total,
        )

    def get_id_by_slug(self, slug: str) -> uuid.UUID:
        """Return the ID of the character with this current or old slug.

        Raises:
            CharacterFacade.NotFoundError: when neither matches.
        """
        character_id = self.db_session.scalars(
            select(CharacterDB.id)
            .where(self._character_has_slug(slug))
            .order_by(self._current_slug_first(CharacterDB.slug, slug))
            .limit(1)
        ).first()
        if character_id is None:
            raise CharacterFacade.NotFoundError(
                f"Character record with ``slug='{slug}'`` not found"
            )
        return character_id

    def get_one_by_slug(self, slug: str) -> CharacterDetailEntity:
        """Return a character with their works and piloted suits.

        An old slug finds the renamed character (D2). Three statements,
        however many rows the lists hold (PYTEST-24).

        Raises:
            CharacterFacade.NotFoundError: when no slug matches.
        """
        character = self.db_session.scalars(
            select(CharacterDB)
            .where(self._character_has_slug(slug))
            .order_by(self._current_slug_first(CharacterDB.slug, slug))
            .limit(1)
        ).first()
        if character is None:
            raise CharacterFacade.NotFoundError(
                f"Character record with ``slug='{slug}'`` not found"
            )
        return CharacterDetailEntity.model_validate(
            {
                **CharacterCardEntity.model_validate(character).model_dump(),
                "appearances": self._get_appearances(character.id),
                "piloted_mobile_suits": self._get_piloted(character.id),
            }
        )

    def create_or_update(self, *, payload: Mapping[str, Any]) -> CharacterEntity:
        """Upsert a character on their slug (SQLA-25)."""
        character = self._upsert(
            CharacterDB, payload=payload, conflict_columns=["slug"]
        )
        return CharacterEntity.model_validate(character)

    def create_or_update_appearance(
        self, *, payload: Mapping[str, Any]
    ) -> CharacterAppearanceEntity:
        """Upsert a character's appearance in a work, on the pair."""
        appearance = self._upsert(
            CharacterAppearanceDB,
            payload=payload,
            conflict_columns=["character_id", "work_id"],
        )
        return CharacterAppearanceEntity.model_validate(appearance)

    def create_or_update_slug_redirect(
        self, *, payload: Mapping[str, Any]
    ) -> CharacterSlugRedirectEntity:
        """Upsert an old slug, pointing it at a character (D2)."""
        redirect = self._upsert(
            CharacterSlugRedirectDB, payload=payload, conflict_columns=["old_slug"]
        )
        return CharacterSlugRedirectEntity.model_validate(redirect)

    @classmethod
    def _character_has_slug(cls, slug: str) -> ColumnElement[bool]:
        """Match the character with this current or old slug (D2)."""
        return cls._has_slug(
            CharacterDB.slug,
            CharacterDB.id,
            CharacterSlugRedirectDB.old_slug,
            CharacterSlugRedirectDB.character_id,
            slug,
        )

    def _get_appearances(self, character_id: uuid.UUID) -> list[CitedWorkEntity]:
        """Return the character's works, first released first."""
        appearances = self.db_session.scalars(
            select(CharacterAppearanceDB)
            .join(CharacterAppearanceDB.work)
            .options(
                contains_eager(CharacterAppearanceDB.work).joinedload(
                    WorkDB.continuity
                ),
                joinedload(CharacterAppearanceDB.source),
            )
            .where(CharacterAppearanceDB.character_id == character_id)
            .order_by(WorkDB.start_date.asc().nulls_last(), WorkDB.title, WorkDB.slug)
        ).all()
        return [
            CitedWorkEntity.model_validate(
                {
                    "created_at": appearance.created_at,
                    "source": SourceCitationEntity.model_validate(appearance.source),
                    "work": WorkCardEntity.model_validate(appearance.work),
                }
            )
            for appearance in appearances
        ]

    def _get_piloted(self, character_id: uuid.UUID) -> list[PilotedMobileSuitEntity]:
        """Return the suits the character pilots, by work, then by name.

        Pairings with no recorded work come after the ones with a work.
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
                MobileSuitPilotDB.work_id.is_(None),
                WorkDB.start_date.asc().nulls_last(),
                WorkDB.title,
                MobileSuitDB.name,
                MobileSuitDB.id,
            )
        ).all()
        return [
            PilotedMobileSuitEntity.model_validate(
                {
                    "created_at": pilot.created_at,
                    "mobile_suit": MobileSuitCardEntity.model_validate(suit),
                    "source": SourceCitationEntity.model_validate(pilot.source),
                    "work": optional_work_ref(work),
                }
            )
            for pilot, suit, work in rows
        ]
