
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PropertyMediaCreate(BaseModel):
    property_id: int

    media_type: str = Field(
        max_length=30,
    )

    url: str

    thumbnail_url: str | None = None

    title: str | None = Field(
        default=None,
        max_length=200,
    )

    sort_order: int = Field(
        default=0,
        ge=0,
    )

    is_primary: bool = False


class PropertyMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    media_type: str
    url: str
    thumbnail_url: str | None
    title: str | None
    sort_order: int
    is_primary: bool
    created_at: datetime


class PropertyDocumentCreate(BaseModel):
    property_id: int

    document_type: str = Field(
        min_length=2,
        max_length=100,
    )

    document_url: str

    remarks: str | None = None


class PropertyDocumentUpdate(BaseModel):
    verification_status: str = Field(
        pattern="^(PENDING|VERIFIED|REJECTED)$"
    )

    remarks: str | None = None


class PropertyDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    document_type: str
    document_url: str
    verification_status: str
    remarks: str | None
    created_at: datetime


class ProjectMediaCreate(BaseModel):
    project_id: int

    media_type: str = Field(
        max_length=30,
    )

    url: str

    thumbnail_url: str | None = None

    title: str | None = Field(
        default=None,
        max_length=200,
    )

    sort_order: int = Field(
        default=0,
        ge=0,
    )

    is_primary: bool = False


class ProjectMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    media_type: str
    url: str
    thumbnail_url: str | None
    title: str | None
    sort_order: int
    is_primary: bool
    created_at: datetime