
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =========================
# COUNTRY
# =========================

class CountryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    iso_code: str | None = Field(
        default=None,
        max_length=10,
    )

    phone_code: str | None = Field(
        default=None,
        max_length=10,
    )


class CountryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    iso_code: str | None = Field(
        default=None,
        max_length=10,
    )

    phone_code: str | None = Field(
        default=None,
        max_length=10,
    )


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    iso_code: str | None
    phone_code: str | None
    created_at: datetime


# =========================
# STATE
# =========================

class StateCreate(BaseModel):
    country_id: int

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    state_code: str | None = Field(
        default=None,
        max_length=20,
    )


class StateUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    state_code: str | None = Field(
        default=None,
        max_length=20,
    )


class StateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    country_id: int
    name: str
    state_code: str | None
    created_at: datetime


# =========================
# CITY
# =========================

class CityCreate(BaseModel):
    state_id: int

    name: str = Field(
        min_length=2,
        max_length=100,
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


class CityUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
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


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    state_id: int
    name: str
    latitude: float | None
    longitude: float | None
    created_at: datetime


# =========================
# LOCALITY
# =========================

class LocalityCreate(BaseModel):
    city_id: int

    name: str = Field(
        min_length=2,
        max_length=150,
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


class LocalityUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
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


class LocalityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city_id: int
    name: str
    pincode: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime


# =========================
# SUB LOCALITY
# =========================

class SubLocalityCreate(BaseModel):
    locality_id: int

    name: str = Field(
        min_length=2,
        max_length=150,
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


class SubLocalityUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
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


class SubLocalityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    locality_id: int
    name: str
    pincode: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime