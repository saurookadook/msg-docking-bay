"""Routes for organizations and their suits (FAPI-4)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, Query

from api.dependencies.db_session import DBSessionDep
from api.models.organization import (
    OrganizationMobileSuitsListResponse,
    OrganizationResponse,
    OrganizationsListResponse,
)
from api.models.pagination import PageLimit, PageMeta, PageOffset
from api.routes.handlers.reads import run_read
from constants.catalog import MobileSuitOrganizationRole
from constants.pagination import DEFAULT_PAGE_SIZE, MAX_SEARCH_LENGTH
from models.mixins.checks import SLUG_PATTERN
from models.organization.facade import OrganizationFacade

logger = logging.getLogger(__name__)

organizations_router = APIRouter(prefix="/api")

type OrganizationSlug = Annotated[
    str,
    Path(
        pattern=SLUG_PATTERN, description="The organization's current or an old slug."
    ),
]


@organizations_router.get("/organizations")
def read_organizations_list(
    api_db_session: DBSessionDep,
    *,
    work: Annotated[
        str | None, Query(description="Only organizations in this work (its slug).")
    ] = None,
    q: Annotated[
        str | None,
        Query(
            max_length=MAX_SEARCH_LENGTH,
            description=(
                "Search slugs, ignoring case, spaces and punctuation: "
                "`zeon` finds the Principality of Zeon. Prefix matches come first."
            ),
        ),
    ] = None,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> OrganizationsListResponse:
    """Return one page of organizations, by name, each with its parent.

    A page past the end is 200 with an empty ``data`` and the real
    ``total`` (D3). Reads only, and calls no external API.
    """
    page = run_read(
        lambda: OrganizationFacade(db_session=api_db_session).get_page(
            work_slug=work, q=q, limit=limit, offset=offset
        ),
        error_detail="Error fetching organizations",
        logger=logger,
    )
    return OrganizationsListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )


@organizations_router.get("/organizations/{organization_slug}")
def read_organization(
    organization_slug: OrganizationSlug, api_db_session: DBSessionDep
) -> OrganizationResponse:
    """Return an organization with its parent, units and works.

    Its suits are a separate, paginated route, since one organization
    can have hundreds (Q1). An old slug returns 200 with the renamed
    organization, whose ``slug`` is the current one (D2). Reads only,
    and calls no external API.
    """
    organization = run_read(
        lambda: OrganizationFacade(db_session=api_db_session).get_one_by_slug(
            organization_slug
        ),
        error_detail="Error fetching organization",
        logger=logger,
        not_found=OrganizationFacade.NotFoundError,
        not_found_detail="Organization not found",
    )
    return OrganizationResponse(data=organization)


@organizations_router.get("/organizations/{organization_slug}/mobile-suits")
def read_organization_mobile_suits(
    organization_slug: OrganizationSlug,
    api_db_session: DBSessionDep,
    *,
    role: Annotated[
        MobileSuitOrganizationRole | None,
        Query(description="Only suits with this role, and only those links."),
    ] = None,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> OrganizationMobileSuitsListResponse:
    """Return one page of an organization's suits, by name.

    One item per suit, with its links (role, work and source) grouped;
    ``total`` counts suits (Q7). An unknown organization is a 404; a
    known one with no suits is 200 with an empty ``data`` (FAPI-12).
    Reads only, and calls no external API.
    """
    page = run_read(
        lambda: OrganizationFacade(db_session=api_db_session).get_mobile_suit_page(
            organization_slug, role=role, limit=limit, offset=offset
        ),
        error_detail="Error fetching the organization's mobile suits",
        logger=logger,
        not_found=OrganizationFacade.NotFoundError,
        not_found_detail="Organization not found",
    )
    return OrganizationMobileSuitsListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )
