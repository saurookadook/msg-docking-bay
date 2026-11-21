"""Field mixins shared by several entities (PYD-2)."""

import uuid

from pydantic import AwareDatetime, BaseModel


class IdEntityMixin(BaseModel):
    """Add the row's ``id``, for full entities only.

    Read models served to clients leave it out: it changes on a
    reseed, and slugs are the public key (catalog-read-api.md D2).
    """

    id: uuid.UUID


class CreatedAtEntityMixin(BaseModel):
    """Add ``created_at``: when this database created the row.

    It says nothing about when the source page was edited; the row's
    source carries that (``retrieved_at``, ``revision_id``).
    """

    created_at: AwareDatetime


class TimestampsEntityMixin(CreatedAtEntityMixin):
    """Add ``updated_at``: when this database last changed the row.

    Upserts leave it alone when nothing changed (sqlalchemy.md SQLA-25).
    """

    updated_at: AwareDatetime
