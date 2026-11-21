"""Routes for mobile suits (FAPI-4)."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from api.dependencies.db_session import DBSessionDep
from api.models.mobile_suit import MobileSuitResponse, MobileSuitsListResponse
from api.models.pagination import PageLimit, PageMeta, PageOffset
from constants.catalog import UnitType
from constants.pagination import DEFAULT_PAGE_SIZE
from models.mixins.checks import SLUG_PATTERN
from models.mobile_suit.facade import MobileSuitFacade

logger = logging.getLogger(__name__)

mobile_suits_router = APIRouter(prefix="/api")

MAX_SEARCH_LENGTH = 100
"""The longest ``q`` accepted; a longer one is a 422 (D8)."""


@mobile_suits_router.get("/mobile-suits")
def read_mobile_suits_list(
    api_db_session: DBSessionDep,
    continuity: Annotated[
        str | None, Query(description="Only suits in this continuity (its slug).")
    ] = None,
    work: Annotated[
        str | None, Query(description="Only suits that appear in this work (its slug).")
    ] = None,
    unit_type: Annotated[
        UnitType | None, Query(description="Only suits of this unit type.")
    ] = None,
    q: Annotated[
        str | None,
        Query(
            max_length=MAX_SEARCH_LENGTH,
            description=(
                "Search slugs and model numbers, ignoring case, spaces and "
                "punctuation: `rx782` finds RX-78-2. Prefix matches come first."
            ),
        ),
    ] = None,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> MobileSuitsListResponse:
    """Return one page of mobile suits, by name.

    A ``q`` with no letters or digits is no filter, so an empty search
    box lists everything (D8). A page past the end is 200 with an empty
    ``data`` and the real ``total``. Reads only, and calls no external
    API.
    """
    try:
        page = MobileSuitFacade(db_session=api_db_session).get_page(
            continuity_slug=continuity,
            work_slug=work,
            unit_type=unit_type,
            q=q,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        error_detail = "Error fetching mobile suits"
        logger.exception(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        ) from e
    return MobileSuitsListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )


@mobile_suits_router.get("/mobile-suits/{mobile_suit_slug}")
def read_mobile_suit(
    mobile_suit_slug: Annotated[
        str,
        Path(pattern=SLUG_PATTERN, description="The suit's current or an old slug."),
    ],
    api_db_session: DBSessionDep,
) -> MobileSuitResponse:
    """Return a suit with its spec sheets, relations and appearances.

    Each fact carries its source, for attribution (D6). Named spec
    sheets are filled from the same source's base sheet, and list the
    columns they took. An old slug returns 200 with the renamed suit,
    whose ``slug`` is the current one (D2). Reads only.
    """
    try:
        suit = MobileSuitFacade(db_session=api_db_session).get_one_by_slug(
            mobile_suit_slug
        )
    except MobileSuitFacade.NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mobile suit not found"
        ) from e
    except Exception as e:
        error_detail = "Error fetching mobile suit"
        logger.exception(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        ) from e
    return MobileSuitResponse(data=suit)
