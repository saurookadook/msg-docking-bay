"""Response models for works (FAPI-12)."""

from api.models.base import BaseResponseModel
from api.models.pagination import PageMeta
from models.mobile_suit.entity import MobileSuitAppearanceCardEntity
from models.work.entity import WorkCardEntity, WorkDetailEntity


class WorksListResponse(BaseResponseModel):
    """One page of works."""

    data: list[WorkCardEntity]
    meta: PageMeta


class WorkResponse(BaseResponseModel):
    """One work, with its parent and relations."""

    data: WorkDetailEntity


class WorkMobileSuitsListResponse(BaseResponseModel):
    """One page of the suits that appear in a work."""

    data: list[MobileSuitAppearanceCardEntity]
    meta: PageMeta
