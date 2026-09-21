
# app/modules/agents/schemas.py

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
)


class AgentCreate(BaseModel):
    user_id: int

    agency_name: str | None = Field(
        default=None,
        max_length=200,
    )

    description: str | None = None

    license_number: str | None = Field(
        default=None,
        max_length=100,
    )

    experience_years: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    rera_registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    website: HttpUrl | None = None


class AgentProfileCreate(BaseModel):
    agency_name: str | None = Field(
        default=None,
        max_length=200,
    )

    description: str | None = None

    license_number: str | None = Field(
        default=None,
        max_length=100,
    )

    experience_years: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    rera_registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    website: HttpUrl | None = None



class AgentUpdate(BaseModel):
    agency_name: str | None = Field(
        default=None,
        max_length=200,
    )

    description: str | None = None

    license_number: str | None = Field(
        default=None,
        max_length=100,
    )

    experience_years: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    rera_registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    website: HttpUrl | None = None

    profile_image: str | None = None


class AgentVerificationUpdate(BaseModel):
    verification_status: str = Field(
        pattern="^(PENDING|VERIFIED|REJECTED|SUSPENDED)$"
    )

    verification_document: str | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    agency_name: str | None
    description: str | None
    license_number: str | None
    experience_years: int
    profile_image: str | None
    verification_status: str
    verification_document: str | None
    rera_registration_number: str | None
    phone: str | None
    email: EmailStr | None
    website: str | None
    is_featured: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AgentListResponse(BaseModel):
    items: list[AgentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


from app.modules.properties.schemas import PropertyCreate, PropertyResponse  # noqa: E402


class AgentBulkPropertyCreate(BaseModel):
    properties: list[PropertyCreate] = Field(
        ...,
        min_length=1,
        description="List of properties to create for this agent",
    )


class AgentBulkPropertyResponse(BaseModel):
    created_count: int
    properties: list[PropertyResponse]