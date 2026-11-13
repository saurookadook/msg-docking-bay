"""The ``organization_appearances`` table: an organization's works."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.db import CreatedAtDB


class OrganizationAppearanceDB(JunctionBaseDB, CreatedAtDB):
    """An organization's appearance in one work, keyed on the pair.

    ``mobile_suit_organizations`` references these rows through a
    composite foreign key, so "operated in work W" implies the
    organization appears in W. Like every appearance, it cites its
    source.
    """

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    """Indexed: it does not lead the primary key (RDB-18)."""
