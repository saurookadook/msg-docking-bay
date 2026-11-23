"""Response models for the catalog search (FAPI-12)."""

from pydantic import BaseModel

from api.models.base import BaseResponseModel
from models.search.entity import CatalogSearchResultsEntity, CatalogSearchTotals


class CatalogSearchMeta(BaseModel):
    """The per-kind limit, and each kind's total (catalog-search.md Q1).

    A plain model, like ``PageMeta``, so its fields stay ``snake_case``.
    """

    limit: int
    totals: CatalogSearchTotals


class CatalogSearchResponse(BaseResponseModel):
    """The first matches of each kind, with every kind's total."""

    data: CatalogSearchResultsEntity
    meta: CatalogSearchMeta
