"""The route that searches the whole catalog (FAPI-4)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Query

from api.dependencies.db_session import DBSessionDep
from api.models.search import CatalogSearchMeta, CatalogSearchResponse
from api.routes.handlers.reads import run_read
from constants.pagination import (
    MAX_SEARCH_LENGTH,
    SEARCH_DEFAULT_LIMIT,
    SEARCH_MAX_LIMIT,
)
from models.search.facade import CatalogSearchFacade

logger = logging.getLogger(__name__)

search_router = APIRouter(prefix="/api")


@search_router.get("/search")
def read_search(
    api_db_session: DBSessionDep,
    *,
    q: Annotated[
        str | None,
        Query(
            max_length=MAX_SEARCH_LENGTH,
            description=(
                "Search every kind as its own list's `q` does: slugs, names and "
                "model numbers, ignoring case, spaces and punctuation. Prefix "
                "matches come first. A blank `q` lists the first rows of each."
            ),
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=SEARCH_MAX_LIMIT,
            description="Results per kind, at most 20.",
        ),
    ] = SEARCH_DEFAULT_LIMIT,
) -> CatalogSearchResponse:
    """Return the first matches of each kind, with every kind's total.

    The kinds are mobile suits, characters, organizations, mechanical
    designers and works. ``meta.totals`` counts every match, so the
    frontend can link to the kind's list with the same ``q`` for the
    rest. Reads only, and calls no external API.
    """
    search = run_read(
        lambda: CatalogSearchFacade(db_session=api_db_session).search(q=q, limit=limit),
        error_detail="Error searching the catalog",
        logger=logger,
    )
    return CatalogSearchResponse(
        data=search.results,
        meta=CatalogSearchMeta(limit=limit, totals=search.totals),
    )
