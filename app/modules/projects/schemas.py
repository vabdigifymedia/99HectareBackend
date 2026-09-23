
from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from app.modules.amenities.schemas import AmenityResponse
from app.modules.media.schemas import ProjectMediaResponse

class ProjectCreate(BaseModel):
    builder_id: int

    name: str = Field(
        min_length=2,
        max_length=250,
    )

    description: str | None = None

    project_type: str = Field(
        min_length=2,
        max_length=50,
    )

    status: str = Field(
        min_length=2,
        max_length=50,
    )

    price_from: Decimal | None = Field(
        default=None,
        gt=0,
    )

    price_to: Decimal | None = Field(
        default=None,
        gt=0,
    )

    total_units: int | None = Field(
        default=None,
        ge=0,
    )

    total_towers: int | None = Field(
        default=None,
        ge=0,
    )

    possession_date: date | None = None

    country_id: int | None = None
    state_id: int | None = None
    city_id: int | None = None
    locality_id: int | None = None

    address: str | None = None

    landmark: str | None = Field(
        default=None,
        max_length=250,
    )

    pincode: str | None = Field(
        default=None,
        max_length=20,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    rera_number: str | None = Field(
        default=None,
        max_length=150,
    )


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=250,
    )

    description: str | None = None

    project_type: str | None = None

    status: str | None = None

    price_from: Decimal | None = Field(
        default=None,
        gt=0,
    )

    price_to: Decimal | None = Field(
        default=None,
        gt=0,
    )

    total_units: int | None = Field(
        default=None,
        ge=0,
    )

    total_towers: int | None = Field(
        default=None,
        ge=0,
    )

    possession_date: date | None = None

    locality_id: int | None = None
    address: str | None = None
    landmark: str | None = None
    pincode: str | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    rera_number: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    builder_id: int
    name: str
    description: str | None
    project_type: str
    status: str
    price_from: Decimal | None
    price_to: Decimal | None
    total_units: int | None
    total_towers: int | None
    possession_date: date | None

    country_id: int | None
    state_id: int | None
    city_id: int | None
    locality_id: int | None

    address: str | None
    landmark: str | None
    pincode: str | None

    latitude: float | None
    longitude: float | None

    rera_number: str | None = None

    slug: str | None = None
    media: list[ProjectMediaResponse] = []
    amenities: list[AmenityResponse] = []

    created_at: datetime
    updated_at: datetime


class ProjectUnitCreate(BaseModel):
    project_id: int

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    configuration: str | None = Field(
        default=None,
        max_length=50,
    )

    bedrooms: int | None = Field(
        default=None,
        ge=0,
    )

    bathrooms: int | None = Field(
        default=None,
        ge=0,
    )

    area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    area_unit: str = Field(
        default="SQFT",
        max_length=20,
    )

    price_from: Decimal | None = Field(
        default=None,
        gt=0,
    )

    price_to: Decimal | None = Field(
        default=None,
        gt=0,
    )

    total_units: int | None = Field(
        default=None,
        ge=0,
    )

    available_units: int | None = Field(
        default=None,
        ge=0,
    )


class ProjectUnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    configuration: str | None
    bedrooms: int | None
    bathrooms: int | None
    area: Decimal | None
    area_unit: str
    price_from: Decimal | None
    price_to: Decimal | None
    total_units: int | None
    available_units: int | None
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    units: list[ProjectUnitResponse] = []