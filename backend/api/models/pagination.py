"""Pagination parameters and metadata shared by list routes (D3)."""

from typing import Annotated

from fastapi import Query
from pydantic import BaseModel

from constants.pagination import MAX_PAGE_SIZE

type PageLimit = Annotated[
    int, Query(ge=1, le=MAX_PAGE_SIZE, description="Rows per page, at most 100.")
]
type PageOffset = Annotated[int, Query(ge=0, description="Rows to skip.")]


class PageMeta(BaseModel):
    """Where a page sits in its list (fastapi.md FAPI-12).

    A plain model, not an envelope, so its fields stay ``snake_case``.
    ``total`` counts every row the filters match, across every page.
    """

    limit: int
    offset: int
    total: int
