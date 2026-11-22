"""Response models for organizations (FAPI-12)."""

from api.models.base import BaseResponseModel
from api.models.pagination import PageMeta
from models.mobile_suit.entity import OrganizationMobileSuitEntity
from models.organization.entity import OrganizationCardEntity, OrganizationDetailEntity


class OrganizationsListResponse(BaseResponseModel):
    """One page of organizations."""

    data: list[OrganizationCardEntity]
    meta: PageMeta


class OrganizationResponse(BaseResponseModel):
    """One organization, with its parent, units and works."""

    data: OrganizationDetailEntity


class OrganizationMobileSuitsListResponse(BaseResponseModel):
    """One page of an organization's suits, each with its links."""

    data: list[OrganizationMobileSuitEntity]
    meta: PageMeta
