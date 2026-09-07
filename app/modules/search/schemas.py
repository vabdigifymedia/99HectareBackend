
from decimal import Decimal

from pydantic import BaseModel, Field


class PropertySearchRequest(BaseModel):
    city_id: int | None = None

    locality_id: int | None = None

    sub_locality_id: int | None = None

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

    bathrooms: int | None = Field(
        default=None,
        ge=0,
    )

    furnishing_status: str | None = None

    construction_status: str | None = None

    facing: str | None = None

    min_floor: int | None = None

    max_floor: int | None = None

    parking_spaces: int | None = Field(
        default=None,
        ge=0,
    )

    builder_id: int | None = None

    agent_id: int | None = None

    project_id: int | None = None

    is_verified: bool | None = None

    is_featured: bool | None = None

    keyword: str | None = Field(
        default=None,
        max_length=200,
    )

    sort_by: str = Field(
        default="created_at",
        pattern="^(created_at|price|price_per_sqft|area)$",
    )

    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
    )

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class PropertySearchResponse(BaseModel):
    items: list

    total: int

    page: int

    page_size: int

    total_pages: int