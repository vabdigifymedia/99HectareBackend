
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class SavedSearchCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    city_id: int | None = None

    locality_id: int | None = None

    property_type: str | None = Field(
        default=None,
        max_length=50,
    )

    listing_type: str | None = Field(
        default=None,
        max_length=30,
    )

    min_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    min_area: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_area: Decimal | None = Field(
        default=None,
        ge=0,
    )

    bedrooms: int | None = Field(
        default=None,
        ge=0,
    )

    furnishing_status: str | None = None

    filters: dict | None = None

    notify_new_listings: bool = False


class SavedSearchUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    min_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    min_area: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_area: Decimal | None = Field(
        default=None,
        ge=0,
    )

    bedrooms: int | None = Field(
        default=None,
        ge=0,
    )

    furnishing_status: str | None = None

    filters: dict | None = None

    notify_new_listings: bool | None = None

    is_active: bool | None = None


class SavedSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str

    city_id: int | None
    locality_id: int | None

    property_type: str | None
    listing_type: str | None

    min_price: Decimal | None
    max_price: Decimal | None

    min_area: Decimal | None
    max_area: Decimal | None

    bedrooms: int | None
    furnishing_status: str | None

    filters: dict | None

    notify_new_listings: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime


class SavedSearchListResponse(BaseModel):
    items: list[SavedSearchResponse]
    total: int
    page: int
    page_size: int