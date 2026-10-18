"""Response models for the health check."""

from typing import Literal

from pydantic import BaseModel

from api.models.base import BaseResponseModel


class HealthCheckStatus(BaseModel):
    """The state the health check reports."""

    status: Literal["ok"]


class HealthCheckResponse(BaseResponseModel):
    """The health check's envelope."""

    data: HealthCheckStatus
