"""Response models for mechanical designers (FAPI-12)."""

from api.models.base import BaseResponseModel
from api.models.pagination import PageMeta
from models.mechanical_designer.entity import (
    MechanicalDesignerCardEntity,
    MechanicalDesignerDetailEntity,
)
from models.mobile_suit.entity import DesignedMobileSuitEntity


class MechanicalDesignersListResponse(BaseResponseModel):
    """One page of mechanical designers."""

    data: list[MechanicalDesignerCardEntity]
    meta: PageMeta


class MechanicalDesignerResponse(BaseResponseModel):
    """One mechanical designer."""

    data: MechanicalDesignerDetailEntity


class MechanicalDesignerMobileSuitsListResponse(BaseResponseModel):
    """One page of the suits a designer is credited with."""

    data: list[DesignedMobileSuitEntity]
    meta: PageMeta
