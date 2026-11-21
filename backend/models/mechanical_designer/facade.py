"""Data access for ``mechanical_designers`` (SQLA-16)."""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import joinedload

from models.base.facade import BaseFacade, normalize_search
from models.base.page import Page
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mechanical_designer.entity import (
    MechanicalDesignerCardEntity,
    MechanicalDesignerEntity,
)
from models.mechanical_designer_slug_redirect.db import (
    MechanicalDesignerSlugRedirectDB,
)
from models.mechanical_designer_slug_redirect.entity import (
    MechanicalDesignerSlugRedirectEntity,
)
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import DesignedMobileSuitEntity, MobileSuitCardEntity
from models.mobile_suit_designer.db import MobileSuitDesignerDB
from models.source.entity import SourceCitationEntity


class MechanicalDesignerFacade(BaseFacade):
    """Read and write mechanical designers and their old slugs."""

    class NotFoundError(Exception):
        """No designer has the slug, as a current or an old one."""

    def get_page(
        self, *, q: str | None = None, limit: int, offset: int
    ) -> Page[MechanicalDesignerCardEntity]:
        """Return one page of designers, by name (D3).

        ``q`` matches the normalized slug, prefix matches first (D8).
        """
        filters: list[ColumnElement[bool]] = []
        order: list[ColumnElement[Any]] = []
        needle = normalize_search(q)
        if needle is not None:
            filters.append(self._search_filter((MechanicalDesignerDB.slug,), needle))
            order.append(self._prefix_rank((MechanicalDesignerDB.slug,), needle))

        designers = self.db_session.scalars(
            select(MechanicalDesignerDB)
            .where(*filters)
            .order_by(*order, MechanicalDesignerDB.name, MechanicalDesignerDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(MechanicalDesignerDB).where(*filters)
        ).scalar_one()
        return Page[MechanicalDesignerCardEntity](
            items=[
                MechanicalDesignerCardEntity.model_validate(row) for row in designers
            ],
            total=total,
        )

    def get_id_by_slug(self, slug: str) -> uuid.UUID:
        """Return the ID of the designer with this current or old slug.

        Raises:
            MechanicalDesignerFacade.NotFoundError: on no match.
        """
        designer = self._find_by_slug(slug)
        return designer.id

    def get_one_by_slug(self, slug: str) -> MechanicalDesignerCardEntity:
        """Return a designer by any of their slugs (D2).

        Raises:
            MechanicalDesignerFacade.NotFoundError: on no match.
        """
        return MechanicalDesignerCardEntity.model_validate(self._find_by_slug(slug))

    def get_mobile_suit_page(
        self, slug: str, *, limit: int, offset: int
    ) -> Page[DesignedMobileSuitEntity]:
        """Return one page of the suits a designer is credited with.

        By suit name. Three statements: the slug, the page and the
        count (PYTEST-24).

        Raises:
            MechanicalDesignerFacade.NotFoundError: on no match.
        """
        designer_id = self.get_id_by_slug(slug)
        credited = MobileSuitDesignerDB.mechanical_designer_id == designer_id
        rows = self.db_session.execute(
            select(MobileSuitDesignerDB, MobileSuitDB)
            .join(MobileSuitDB, MobileSuitDB.id == MobileSuitDesignerDB.mobile_suit_id)
            .options(
                joinedload(MobileSuitDesignerDB.source),
                joinedload(MobileSuitDB.continuity),
            )
            .where(credited)
            .order_by(MobileSuitDB.name, MobileSuitDB.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.db_session.execute(
            select(func.count()).select_from(MobileSuitDesignerDB).where(credited)
        ).scalar_one()
        return Page[DesignedMobileSuitEntity](
            items=[
                DesignedMobileSuitEntity.model_validate(
                    {
                        "created_at": credit.created_at,
                        "mobile_suit": MobileSuitCardEntity.model_validate(suit),
                        "source": SourceCitationEntity.model_validate(credit.source),
                    }
                )
                for credit, suit in rows
            ],
            total=total,
        )

    def create_or_update(
        self, *, payload: Mapping[str, Any]
    ) -> MechanicalDesignerEntity:
        """Upsert a designer on their slug (SQLA-25)."""
        designer = self._upsert(
            MechanicalDesignerDB, payload=payload, conflict_columns=["slug"]
        )
        return MechanicalDesignerEntity.model_validate(designer)

    def create_or_update_slug_redirect(
        self, *, payload: Mapping[str, Any]
    ) -> MechanicalDesignerSlugRedirectEntity:
        """Upsert an old slug, pointing it at a designer (D2)."""
        redirect = self._upsert(
            MechanicalDesignerSlugRedirectDB,
            payload=payload,
            conflict_columns=["old_slug"],
        )
        return MechanicalDesignerSlugRedirectEntity.model_validate(redirect)

    def _find_by_slug(self, slug: str) -> MechanicalDesignerDB:
        """Return the designer row with this current or old slug.

        Raises:
            MechanicalDesignerFacade.NotFoundError: on no match.
        """
        designer = self.db_session.scalars(
            select(MechanicalDesignerDB)
            .where(
                self._has_slug(
                    MechanicalDesignerDB.slug,
                    MechanicalDesignerDB.id,
                    MechanicalDesignerSlugRedirectDB.old_slug,
                    MechanicalDesignerSlugRedirectDB.mechanical_designer_id,
                    slug,
                )
            )
            .order_by(self._current_slug_first(MechanicalDesignerDB.slug, slug))
            .limit(1)
        ).first()
        if designer is None:
            raise MechanicalDesignerFacade.NotFoundError(
                f"Mechanical designer record with ``slug='{slug}'`` not found"
            )
        return designer
