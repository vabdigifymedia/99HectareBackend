
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class InquiryCreate(BaseModel):
    property_id: int | None = None
    project_id: int | None = None

    agent_id: int | None = None
    builder_id: int | None = None

    name: str | None = Field(
        default=None,
        max_length=150,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    message: str | None = None

    source: str | None = Field(
        default=None,
        max_length=50,
    )


class InquiryUpdate(BaseModel):
    status: str | None = Field(
        default=None,
        pattern="^(NEW|CONTACTED|INTERESTED|VISITED|CONVERTED|CLOSED|CANCELLED)$"
    )

    message: str | None = None


class InquiryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    property_id: int | None
    project_id: int | None

    agent_id: int | None
    builder_id: int | None

    name: str | None
    email: EmailStr | None
    phone: str | None

    message: str | None
    status: str
    source: str | None

    created_at: datetime
    updated_at: datetime


class InquiryListResponse(BaseModel):
    items: list[InquiryResponse]
    total: int
    page: int
    page_size: int