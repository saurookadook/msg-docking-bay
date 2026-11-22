"""The ``character_slug_redirects`` table: characters' old slugs."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import slug_format
from models.mixins.db import CreatedAtDB


class CharacterSlugRedirectDB(JunctionBaseDB, CreatedAtDB):
    """A slug a character had before their page was renamed (D2).

    A detail read that misses on ``characters.slug`` looks here, so
    old links keep working. Keyed on the old slug, so it has no
    surrogate ``id`` (RDB-13). A current slug always wins: the loader
    deletes a redirect whose ``old_slug`` a row takes as its own.
    """

    character_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    """CASCADE: a deleted character takes their old slugs along."""
    old_slug: Mapped[str] = mapped_column(primary_key=True)

    __table_args__ = (slug_format("old_slug"),)
