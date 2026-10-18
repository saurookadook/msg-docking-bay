"""Response models for the homepage."""

from pydantic import BaseModel

from api.models.base import BaseResponseModel


class HomeInfo(BaseModel):
    """What the homepage says about the API."""

    message: str
    name: str


class HomeResponse(BaseResponseModel):
    """The homepage's envelope."""

    data: HomeInfo
