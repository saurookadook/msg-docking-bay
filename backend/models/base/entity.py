"""The base every entity and read model inherits from (PYD-2)."""

from pydantic import BaseModel, ConfigDict


class BaseEntityModel(BaseModel):
    """Validate from ORM rows, and list every field the API sends.

    ``id`` is not here: full entities add it with ``IdEntityMixin``,
    and read models served to clients leave it out, because slugs are
    the public key (catalog-read-api.md D5).

    ``json_schema_serialization_defaults_required`` marks a defaulted
    field, such as ``model_number: str | None = None``, as required in
    the response schema. The API always sends the key, so the generated
    client types it ``string | null``, not optional.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_serialization_defaults_required=True,
    )
