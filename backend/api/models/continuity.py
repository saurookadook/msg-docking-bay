"""Response models for continuities (FAPI-12)."""

from api.models.base import BaseResponseModel
from models.continuity.entity import ContinuityCardEntity


class ContinuitiesListResponse(BaseResponseModel):
    """Every continuity. Unpaginated, so it has no ``meta``."""

    data: list[ContinuityCardEntity]
