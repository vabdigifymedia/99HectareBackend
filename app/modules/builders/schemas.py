
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
)


class BuilderCreate(BaseModel):
    user_id: int

    company_name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    website: HttpUrl | None = None

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    license_number: str | None = Field(
        default=None,
        max_length=100,
    )

    rera_registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    established_year: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )


class BuilderUpdate(BaseModel):
    company_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    website: HttpUrl | None = None

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    license_number: str | None = Field(
        default=None,
        max_length=100,
    )

    rera_registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    established_year: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )

    logo: str | None = None


class BuilderVerificationUpdate(BaseModel):
    verification_status: str = Field(
        pattern="^(PENDING|VERIFIED|REJECTED|SUSPENDED)$"
    )

    verification_document: str | None = None


class BuilderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company_name: str
    description: str | None
    website: str | None
    email: EmailStr | None
    phone: str | None
    logo: str | None
    license_number: str | None
    rera_registration_number: str | None
    verification_status: str
    verification_document: str | None
    established_year: int | None
    is_featured: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime