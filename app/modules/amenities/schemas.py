
# app/modules/amenities/schemas.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AmenityCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    icon: str | None = Field(
        default=None,
        max_length=500,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )


class AmenityUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    icon: str | None = Field(
        default=None,
        max_length=500,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    is_active: bool | None = None


class AmenityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    icon: str | None
    category: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AmenityListResponse(BaseModel):
    items: list[AmenityResponse]
    total: int
    page: int
    page_size: int