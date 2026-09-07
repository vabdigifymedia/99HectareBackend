
from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PropertyCreate(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=300,
    )

    description: str | None = None

    property_type: str = Field(
        min_length=2,
        max_length=50,
    )

    listing_type: str = Field(
        min_length=2,
        max_length=30,
    )

    price: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=2,
    )

    price_per_sqft: Decimal | None = Field(
        default=None,
        gt=0,
    )

    maintenance_charge: Decimal | None = Field(
        default=None,
        ge=0,
    )

    security_deposit: Decimal | None = Field(
        default=None,
        ge=0,
    )

    booking_amount: Decimal | None = Field(
        default=None,
        ge=0,
    )

    is_price_negotiable: bool = False

    carpet_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    built_up_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    super_built_up_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    plot_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    area_unit: str = "SQFT"

    bedrooms: int | None = Field(
        default=None,
        ge=0,
    )

    bathrooms: int | None = Field(
        default=None,
        ge=0,
    )

    balconies: int | None = Field(
        default=None,
        ge=0,
    )

    floor_number: int | None = None

    total_floors: int | None = Field(
        default=None,
        ge=0,
    )

    furnishing_status: str | None = None

    facing: str | None = None

    parking_spaces: int | None = Field(
        default=None,
        ge=0,
    )

    property_age: int | None = Field(
        default=None,
        ge=0,
    )

    year_built: int | None = Field(
        default=None,
        ge=1800,
        le=2100,
    )

    construction_status: str | None = None

    possession_date: date | None = None

    country_id: int | None = None
    state_id: int | None = None
    city_id: int | None = None
    locality_id: int | None = None
    sub_locality_id: int | None = None

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

    owner_id: int | None = None
    agent_id: int | None = None
    builder_id: int | None = None
    project_id: int | None = None

    rera_number: str | None = None

    ownership_type: str | None = None


class PropertyUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=5,
        max_length=300,
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    price_per_sqft: Decimal | None = Field(
        default=None,
        gt=0,
    )

    maintenance_charge: Decimal | None = Field(
        default=None,
        ge=0,
    )

    security_deposit: Decimal | None = Field(
        default=None,
        ge=0,
    )

    booking_amount: Decimal | None = Field(
        default=None,
        ge=0,
    )

    is_price_negotiable: bool | None = None

    carpet_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    built_up_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    super_built_up_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    plot_area: Decimal | None = Field(
        default=None,
        gt=0,
    )

    bedrooms: int | None = Field(
        default=None,
        ge=0,
    )

    bathrooms: int | None = Field(
        default=None,
        ge=0,
    )

    balconies: int | None = Field(
        default=None,
        ge=0,
    )

    floor_number: int | None = None
    total_floors: int | None = Field(
        default=None,
        ge=0,
    )

    furnishing_status: str | None = None
    facing: str | None = None

    parking_spaces: int | None = Field(
        default=None,
        ge=0,
    )

    construction_status: str | None = None
    possession_date: date | None = None

    locality_id: int | None = None
    sub_locality_id: int | None = None

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


class PropertyStatusUpdate(BaseModel):
    status: str = Field(
        pattern=(
            "^(DRAFT|PENDING_VERIFICATION|APPROVED|"
            "REJECTED|PUBLISHED|SOLD|RENTED|EXPIRED|ARCHIVED)$"
        )
    )


class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    description: str | None

    property_type: str
    listing_type: str
    status: str

    price: Decimal
    price_per_sqft: Decimal | None

    maintenance_charge: Decimal | None
    security_deposit: Decimal | None
    booking_amount: Decimal | None

    is_price_negotiable: bool

    carpet_area: Decimal | None
    built_up_area: Decimal | None
    super_built_up_area: Decimal | None
    plot_area: Decimal | None
    area_unit: str

    bedrooms: int | None
    bathrooms: int | None
    balconies: int | None

    floor_number: int | None
    total_floors: int | None

    furnishing_status: str | None
    facing: str | None
    parking_spaces: int | None

    property_age: int | None
    year_built: int | None

    construction_status: str | None
    possession_date: date | None

    country_id: int | None
    state_id: int | None
    city_id: int | None
    locality_id: int | None
    sub_locality_id: int | None

    address: str | None
    landmark: str | None
    pincode: str | None

    latitude: float | None
    longitude: float | None

    owner_id: int | None
    agent_id: int | None
    builder_id: int | None
    project_id: int | None

    rera_number: str | None
    ownership_type: str | None

    is_verified: bool
    is_featured: bool
    is_premium: bool
    is_active: bool

    published_at: datetime | None
    expires_at: datetime | None

    created_at: datetime
    updated_at: datetime


class ResidentialPropertyDetailsCreate(BaseModel):
    property_id: int

    servant_room: bool = False
    study_room: bool = False
    pooja_room: bool = False
    store_room: bool = False

    other_room: str | None = None

    electricity_available: bool = True

    water_supply: str | None = None

    gas_pipeline: bool = False


class ResidentialPropertyDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int

    servant_room: bool
    study_room: bool
    pooja_room: bool
    store_room: bool
    other_room: str | None

    electricity_available: bool
    water_supply: str | None
    gas_pipeline: bool


class CommercialPropertyDetailsCreate(BaseModel):
    property_id: int

    commercial_sub_type: str | None = None

    washrooms: int | None = Field(
        default=None,
        ge=0,
    )

    conference_rooms: int | None = Field(
        default=None,
        ge=0,
    )

    cabins: int | None = Field(
        default=None,
        ge=0,
    )

    pantry: bool = False
    reception_area: bool = False
    power_backup: bool = False


class CommercialPropertyDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int

    commercial_sub_type: str | None

    washrooms: int | None
    conference_rooms: int | None
    cabins: int | None

    pantry: bool
    reception_area: bool
    power_backup: bool


class PlotPropertyDetailsCreate(BaseModel):
    property_id: int

    plot_length: Decimal | None = Field(
        default=None,
        gt=0,
    )

    plot_width: Decimal | None = Field(
        default=None,
        gt=0,
    )

    road_width: Decimal | None = Field(
        default=None,
        gt=0,
    )

    boundary_wall: bool = False
    corner_plot: bool = False
    gated_community: bool = False


class PlotPropertyDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int

    plot_length: Decimal | None
    plot_width: Decimal | None
    road_width: Decimal | None

    boundary_wall: bool
    corner_plot: bool
    gated_community: bool