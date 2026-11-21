"""Response models for mobile suits (FAPI-12)."""

from api.models.base import BaseResponseModel
from api.models.pagination import PageMeta
from models.mobile_suit.entity import MobileSuitCardEntity, MobileSuitDetailEntity


class MobileSuitsListResponse(BaseResponseModel):
    """One page of mobile suits."""

    data: list[MobileSuitCardEntity]
    meta: PageMeta


class MobileSuitResponse(BaseResponseModel):
    """One suit, with its spec sheets, relations and appearances."""

    data: MobileSuitDetailEntity
