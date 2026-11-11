"""The ``mobile_suit_organizations`` table: who builds a suit."""

import uuid

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import MobileSuitOrganizationRole
from constants.db_types import MOBILE_SUIT_ORGANIZATION_ROLE_DB_TYPE
from db.base_db import BaseDB
from models.mixins.db import CreatedAtDB


class MobileSuitOrganizationDB(BaseDB, CreatedAtDB):
    """An organization's role for a mobile suit, in one work or none.

    The same deliberate deviation from RDB-2 as ``mobile_suit_pilots``:
    an optional ``work_id`` cannot be in a primary key, so the link has
    a surrogate ``id`` and a ``UNIQUE NULLS NOT DISTINCT`` key. The
    role is in the key, so one organization can both manufacture and
    operate a suit.

    Composite foreign keys tie a row to the appearances, so "operated
    in work W" implies the organization and the suit both appear in W.
    They are MATCH SIMPLE: a null ``work_id`` skips them whole, so
    plain foreign keys check the organization and the suit as well.
    """

    mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE")
    )
    """Led by the (suit, work) index, so not indexed alone."""
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    """Led by the (organization, work) index, so not indexed alone."""
    role: Mapped[MobileSuitOrganizationRole] = mapped_column(
        MOBILE_SUIT_ORGANIZATION_ROLE_DB_TYPE
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    work_id: Mapped[uuid.UUID | None]
    """The work the role is in; null when the page does not say."""

    __table_args__ = (
        # CASCADE: a link needs both appearances it relies on.
        ForeignKeyConstraint(
            ["mobile_suit_id", "work_id"],
            [
                "mobile_suit_appearances.mobile_suit_id",
                "mobile_suit_appearances.work_id",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["organization_id", "work_id"],
            [
                "organization_appearances.organization_id",
                "organization_appearances.work_id",
            ],
            ondelete="CASCADE",
        ),
        # Named here: the ix convention repeats the table name for
        # each column of a multi-column index.
        Index(
            "ix_mobile_suit_organizations_mobile_suit_id_work_id",
            "mobile_suit_id",
            "work_id",
        ),
        Index(
            "ix_mobile_suit_organizations_organization_id_work_id",
            "organization_id",
            "work_id",
        ),
        # Named here: the derived name, 73 characters, is over
        # PostgreSQL's 63-character identifier limit.
        UniqueConstraint(
            "mobile_suit_id",
            "organization_id",
            "role",
            "work_id",
            name="mobile_suit_organizations_link_key",
            postgresql_nulls_not_distinct=True,
        ),
    )
