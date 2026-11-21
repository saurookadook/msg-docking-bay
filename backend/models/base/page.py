"""One page of a list, with the total across every page (D3)."""

from pydantic import BaseModel


class Page[T](BaseModel):
    """Return a facade's page of rows and the unpaginated total.

    The route turns it into ``data`` and ``meta`` (fastapi.md FAPI-12).
    """

    items: list[T]
    total: int
