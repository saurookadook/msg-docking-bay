"""Timestamp columns for entity and junction tables (SQLA-7, RDB-17)."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtDB:
    """Add ``created_at``: junction tables have no ``updated_at``."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class TimestampsDB(CreatedAtDB):
    """Add ``created_at`` and ``updated_at``, for every entity table.

    ``onupdate`` runs only for ORM and Core ``update()`` statements; an
    upsert sets ``updated_at`` itself (SQLA-25).
    """

    updated_at: Mapped[datetime] = mapped_column(
        onupdate=func.now(), server_default=func.now()
    )
