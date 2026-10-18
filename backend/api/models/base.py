"""The base class for response envelopes (PYD-13)."""

from pydantic import BaseModel, ConfigDict, alias_generators


class BaseResponseModel(BaseModel):
    """Base for every response envelope.

    The camelCase alias generator applies only to the envelope's own
    fields, so envelopes use single-word field names (``data``).
    """

    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        from_attributes=True,
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )
