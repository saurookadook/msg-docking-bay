"""The API's homepage."""

import logging

from fastapi import APIRouter

from api.models.home import HomeInfo, HomeResponse

logger = logging.getLogger(__name__)

home_router = APIRouter(prefix="/api")


@home_router.get("")
def read_home() -> HomeResponse:
    """Return the API's name and a welcome message.

    The body is static for now: it calls nothing and writes nothing.
    """
    return HomeResponse(
        data=HomeInfo(
            message="Welcome to the msg-docking-bay API.", name="msg-docking-bay"
        )
    )
