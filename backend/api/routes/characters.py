"""Routes for characters (FAPI-4)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, Query

from api.dependencies.db_session import DBSessionDep
from api.models.character import CharacterResponse, CharactersListResponse
from api.models.pagination import PageLimit, PageMeta, PageOffset
from api.routes.handlers.reads import run_read
from constants.pagination import DEFAULT_PAGE_SIZE, MAX_SEARCH_LENGTH
from models.character.facade import CharacterFacade
from models.mixins.checks import SLUG_PATTERN

logger = logging.getLogger(__name__)

characters_router = APIRouter(prefix="/api")

type CharacterSlug = Annotated[
    str,
    Path(pattern=SLUG_PATTERN, description="The character's current or an old slug."),
]


@characters_router.get("/characters")
def read_characters_list(
    api_db_session: DBSessionDep,
    *,
    work: Annotated[
        str | None, Query(description="Only characters in this work (its slug).")
    ] = None,
    q: Annotated[
        str | None,
        Query(
            max_length=MAX_SEARCH_LENGTH,
            description=(
                "Search slugs and names, ignoring case, spaces and punctuation: "
                "`amuro` finds Amuro Ray. Prefix matches come first."
            ),
        ),
    ] = None,
    limit: PageLimit = DEFAULT_PAGE_SIZE,
    offset: PageOffset = 0,
) -> CharactersListResponse:
    """Return one page of characters, by name.

    A page past the end is 200 with an empty ``data`` and the real
    ``total`` (D3). Reads only, and calls no external API.
    """
    page = run_read(
        lambda: CharacterFacade(db_session=api_db_session).get_page(
            work_slug=work, q=q, limit=limit, offset=offset
        ),
        error_detail="Error fetching characters",
        logger=logger,
    )
    return CharactersListResponse(
        data=page.items, meta=PageMeta(limit=limit, offset=offset, total=page.total)
    )


@characters_router.get("/characters/{character_slug}")
def read_character(
    character_slug: CharacterSlug, api_db_session: DBSessionDep
) -> CharacterResponse:
    """Return a character with their works and the suits they pilot.

    An old slug returns 200 with the renamed character, whose ``slug``
    is the current one; the frontend replaces its URL (D2). Reads only,
    and calls no external API.
    """
    character = run_read(
        lambda: CharacterFacade(db_session=api_db_session).get_one_by_slug(
            character_slug
        ),
        error_detail="Error fetching character",
        logger=logger,
        not_found=CharacterFacade.NotFoundError,
        not_found_detail="Character not found",
    )
    return CharacterResponse(data=character)
