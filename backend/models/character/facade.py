"""Data access for ``characters`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any, Final

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import contains_eager, joinedload

from models.base.facade import BaseFacade, SlugColumns
from models.base.page import Page
from models.character.db import CharacterDB
from models.character.detail import CharacterDetailEntity
from models.character.entity import CharacterCardEntity, CharacterEntity
from models.character_appearance.db import CharacterAppearanceDB
from models.character_appearance.entity import CharacterAppearanceEntity
from models.character_slug_redirect.db import CharacterSlugRedirectDB
from models.character_slug_redirect.entity import CharacterSlugRedirectEntity
from models.mobile_suit_pilot.facade import MobileSuitPilotFacade
from models.source.entity import SourceCitationEntity
from models.work.db import WorkDB
from models.work.entity import CitedWorkEntity, WorkCardEntity

_SLUG_COLUMNS: Final = SlugColumns(
    CharacterDB.slug,
    CharacterDB.id,
    CharacterSlugRedirectDB.old_slug,
    CharacterSlugRedirectDB.character_id,
)


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

        ``q`` matches the normalized slug and name, prefix matches
        first (D8).
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
        search = self._search_clauses(q, (CharacterDB.slug, CharacterDB.name))
        if search is not None:
            filters.append(search.filter)
            order.append(search.rank)

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
        return self._first_by_slug(
            select(CharacterDB.id),
            slug,
            columns=_SLUG_COLUMNS,
            not_found=CharacterFacade.NotFoundError,
            record="Character",
        )

    def get_one_by_slug(self, slug: str) -> CharacterDetailEntity:
        """Return a character with their works and piloted suits.

        An old slug finds the renamed character (D2). Three statements,
        however many rows the lists hold (PYTEST-24).

        Raises:
            CharacterFacade.NotFoundError: when no slug matches.
        """
        character = self._first_by_slug(
            select(CharacterDB),
            slug,
            columns=_SLUG_COLUMNS,
            not_found=CharacterFacade.NotFoundError,
            record="Character",
        )
        return CharacterDetailEntity.model_validate(
            {
                **CharacterCardEntity.model_validate(character).model_dump(),
                "appearances": self._get_appearances(character.id),
                "piloted_mobile_suits": MobileSuitPilotFacade(
                    db_session=self.db_session
                ).get_for_character(character.id),
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
        return self._upsert_slug_redirect(
            CharacterSlugRedirectDB, CharacterSlugRedirectEntity, payload=payload
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
