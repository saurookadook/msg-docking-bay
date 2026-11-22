"""Routes for mechanical designers and their suits (FAPI-4)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, Query

from api.dependencies.db_session import DBSessionDep
from api.models.mechanical_designer import (
    MechanicalDesignerMobileSuitsListResponse,
    MechanicalDesignerResponse,
    MechanicalDesignersListResponse,
)
from api.models.pagination import PageLimit, PageMeta, PageOffset
from api.routes.handlers.reads import run_read
from constants.pagination import DEFAULT_PAGE_SIZE, MAX_SEARCH_LENGTH
from models.mechanical_designer.facade import MechanicalDesignerFacade
from models.mixins.checks import SLUG_PATTERN

logger = logging.getLogger(__name__)

mechanical_designers_router = APIRouter(prefix="/api")

type MechanicalDesignerSlug = Annotated[
    str,
    Path(pattern=SLUG_PATTERN, description="The designer's current or an old slug."),
]


@mechanical_designers_router.get("/mechanical-designers")
def read_mechanical_designers_list(
    api_db_session: DBSessionDep,
    *,
    q: Annotated[
        str | None,
        Query(
            max_length=MAX_SEARCH_LENGTH,
            description=(
                "Search slugs, ignoring case, spaces and punctuation: "
                "`okawara` finds Kunio Okawara. Prefix matches come first."
            ),
        ),
    ] = None,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> MechanicalDesignersListResponse:
    """Return one page of mechanical designers, by name.

    A page past the end is 200 with an empty ``data`` and the real
    ``total`` (D3). Reads only, and calls no external API.
    """
    page = run_read(
        lambda: MechanicalDesignerFacade(db_session=api_db_session).get_page(
            q=q, limit=limit, offset=offset
        ),
        error_detail="Error fetching mechanical designers",
        logger=logger,
    )
    return MechanicalDesignersListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )


@mechanical_designers_router.get("/mechanical-designers/{mechanical_designer_slug}")
def read_mechanical_designer(
    mechanical_designer_slug: MechanicalDesignerSlug, api_db_session: DBSessionDep
) -> MechanicalDesignerResponse:
    """Return a mechanical designer.

    Their suits are a separate, paginated route, since one designer can
    have hundreds (Q1). An old slug returns 200 with the renamed
    designer, whose ``slug`` is the current one (D2). Reads only, and
    calls no external API.
    """
    designer = run_read(
        lambda: MechanicalDesignerFacade(db_session=api_db_session).get_one_by_slug(
            mechanical_designer_slug
        ),
        error_detail="Error fetching mechanical designer",
        logger=logger,
        not_found=MechanicalDesignerFacade.NotFoundError,
        not_found_detail="Mechanical designer not found",
    )
    return MechanicalDesignerResponse(data=designer)


@mechanical_designers_router.get(
    "/mechanical-designers/{mechanical_designer_slug}/mobile-suits"
)
def read_mechanical_designer_mobile_suits(
    mechanical_designer_slug: MechanicalDesignerSlug,
    api_db_session: DBSessionDep,
    *,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> MechanicalDesignerMobileSuitsListResponse:
    """Return one page of the suits credited to a designer, by name.

    Each carries the source that credits the designer. An unknown
    designer is a 404; a known one with no suits is 200 with an empty
    ``data`` (FAPI-12). Reads only, and calls no external API.
    """
    page = run_read(
        lambda: MechanicalDesignerFacade(
            db_session=api_db_session
        ).get_mobile_suit_page(mechanical_designer_slug, limit=limit, offset=offset),
        error_detail="Error fetching the designer's mobile suits",
        logger=logger,
        not_found=MechanicalDesignerFacade.NotFoundError,
        not_found_detail="Mechanical designer not found",
    )
    return MechanicalDesignerMobileSuitsListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )
