
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ReportCreate(BaseModel):
    property_id: int | None = None

    agent_id: int | None = None

    builder_id: int | None = None

    reported_user_id: int | None = None

    reason: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = None


class ReportUpdate(BaseModel):
    status: str | None = Field(
        default=None,
        pattern="^(OPEN|UNDER_REVIEW|RESOLVED|REJECTED)$"
    )

    admin_notes: str | None = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter_id: int

    property_id: int | None
    agent_id: int | None
    builder_id: int | None
    reported_user_id: int | None

    reason: str
    description: str | None

    status: str

    admin_notes: str | None

    resolved_by: int | None
    resolved_at: datetime | None

    created_at: datetime
    updated_at: datetime


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    page_size: int