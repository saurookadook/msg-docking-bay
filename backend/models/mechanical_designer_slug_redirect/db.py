"""The ``mechanical_designer_slug_redirects`` table: old slugs."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import slug_format
from models.mixins.db import CreatedAtDB


class MechanicalDesignerSlugRedirectDB(JunctionBaseDB, CreatedAtDB):
    """A designer's slug from before their page was renamed (D2).

    A detail read that misses on ``mechanical_designers.slug`` looks
    here, so old links keep working. Keyed on the old slug, so it has no
    surrogate ``id`` (RDB-13). A current slug always wins: the loader
    deletes a redirect whose ``old_slug`` a row takes as its own.
    """

    mechanical_designer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mechanical_designers.id", ondelete="CASCADE"), index=True
    )
    """CASCADE: a deleted designer takes their old slugs along."""
    old_slug: Mapped[str] = mapped_column(primary_key=True)

    __table_args__ = (slug_format("old_slug"),)
