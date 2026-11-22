"""The ``organization_slug_redirects`` table: old slugs."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import slug_format
from models.mixins.db import CreatedAtDB


class OrganizationSlugRedirectDB(JunctionBaseDB, CreatedAtDB):
    """A slug an organization had before its page was renamed (D2).

    A detail read that misses on ``organizations.slug`` looks here, so
    old links keep working. Keyed on the old slug, so it has no
    surrogate ``id`` (RDB-13). A current slug always wins: the loader
    deletes a redirect whose ``old_slug`` a row takes as its own.
    """

    old_slug: Mapped[str] = mapped_column(primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    """CASCADE: a deleted organization takes its old slugs along."""

    __table_args__ = (slug_format("old_slug"),)
