"""Routes for continuities (FAPI-4)."""

import logging

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import DBSessionDep
from api.models.continuity import ContinuitiesListResponse
from models.continuity.facade import ContinuityFacade

logger = logging.getLogger(__name__)

continuities_router = APIRouter(prefix="/api")


@continuities_router.get("/continuities")
def read_continuities_list(api_db_session: DBSessionDep) -> ContinuitiesListResponse:
    """Return every continuity by name, each with its parent continuity.

    Unpaginated: there are a few dozen at most. Reads only, and calls
    no external API.
    """
    try:
        continuities = ContinuityFacade(db_session=api_db_session).get_all()
    except Exception as e:
        error_detail = "Error fetching continuities"
        logger.exception(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        ) from e
    return ContinuitiesListResponse(data=continuities)
