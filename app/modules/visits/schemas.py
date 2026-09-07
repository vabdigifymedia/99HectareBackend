
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisitCreate(BaseModel):
    property_id: int
    requested_date: datetime
    user_notes: str | None = None


class VisitUpdate(BaseModel):
    requested_date: datetime | None = None
    user_notes: str | None = None


class VisitStatusUpdate(BaseModel):
    status: str
    confirmed_date: datetime | None = None
    agent_notes: str | None = None
    cancellation_reason: str | None = None


class VisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    user_id: int
    property_id: int
    agent_id: int | None

    requested_date: datetime
    confirmed_date: datetime | None

    status: str

    user_notes: str | None
    agent_notes: str | None
    cancellation_reason: str | None

    created_at: datetime
    updated_at: datetime


class VisitListResponse(BaseModel):
    items: list[VisitResponse]
    total: int