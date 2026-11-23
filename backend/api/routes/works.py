"""Routes for works and the suits in them (FAPI-4)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, Query

from api.dependencies.db_session import DBSessionDep
from api.models.pagination import PageLimit, PageMeta, PageOffset
from api.models.work import WorkMobileSuitsListResponse, WorkResponse, WorksListResponse
from api.routes.handlers.reads import run_read
from constants.catalog import WorkType
from constants.pagination import DEFAULT_PAGE_SIZE, MAX_SEARCH_LENGTH
from models.mixins.checks import SLUG_PATTERN
from models.mobile_suit.facade import MobileSuitFacade
from models.work.facade import WorkFacade

logger = logging.getLogger(__name__)

works_router = APIRouter(prefix="/api")

type WorkSlug = Annotated[
    str,
    Path(pattern=SLUG_PATTERN, description="The work's current or an old slug."),
]


@works_router.get("/works")
def read_works_list(
    api_db_session: DBSessionDep,
    *,
    continuity: Annotated[
        str | None, Query(description="Only works in this continuity (its slug).")
    ] = None,
    work_type: Annotated[
        WorkType | None, Query(description="Only works of this type.")
    ] = None,
    q: Annotated[
        str | None,
        Query(
            max_length=MAX_SEARCH_LENGTH,
            description=(
                "Search slugs and titles, ignoring case, spaces and punctuation: "
                "`zeta` finds Mobile Suit Zeta Gundam. Prefix matches come first."
            ),
        ),
    ] = None,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> WorksListResponse:
    """Return one page of works, first released first.

    Works with no known date come last. A page past the end is 200 with
    an empty ``data`` and the real ``total`` (D3). Reads only, and calls
    no external API.
    """
    page = run_read(
        lambda: WorkFacade(db_session=api_db_session).get_page(
            continuity_slug=continuity,
            work_type=work_type,
            q=q,
            limit=limit,
            offset=offset,
        ),
        error_detail="Error fetching works",
        logger=logger,
    )
    return WorksListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )


@works_router.get("/works/{work_slug}")
def read_work(work_slug: WorkSlug, api_db_session: DBSessionDep) -> WorkResponse:
    """Return a work with its continuity, parent work and related works.

    An old slug returns 200 with the renamed work, whose ``slug`` is the
    current one; the frontend replaces its URL (D2). Reads only.
    """
    work = run_read(
        lambda: WorkFacade(db_session=api_db_session).get_one_by_slug(work_slug),
        error_detail="Error fetching work",
        logger=logger,
        not_found=WorkFacade.NotFoundError,
        not_found_detail="Work not found",
    )
    return WorkResponse(data=work)


@works_router.get("/works/{work_slug}/mobile-suits")
def read_work_mobile_suits(
    work_slug: WorkSlug,
    api_db_session: DBSessionDep,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> WorkMobileSuitsListResponse:
    """Return one page of a work's suits, debuts first, then by name.

    Each carries its episode range and whether it debuts in the work.
    An unknown work is a 404; a known one with no suits is 200 with an
    empty ``data`` (FAPI-12). Reads only.
    """
    page = run_read(
        lambda: MobileSuitFacade(db_session=api_db_session).get_page_by_work_slug(
            work_slug, limit=limit, offset=offset
        ),
        error_detail="Error fetching the work's mobile suits",
        logger=logger,
        not_found=WorkFacade.NotFoundError,
        not_found_detail="Work not found",
    )
    return WorkMobileSuitsListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )
