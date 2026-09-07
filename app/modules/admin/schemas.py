
# app/modules/admin/schemas.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminCreate(BaseModel):
    user_id: int
    admin_level: str = Field(
        default="MODERATOR",
        max_length=30,
    )
    department: str | None = Field(
        default=None,
        max_length=100,
    )


class AdminUpdate(BaseModel):
    admin_level: str | None = Field(
        default=None,
        max_length=30,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    is_active: bool | None = None


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    admin_level: str
    department: str | None
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminActionCreate(BaseModel):
    action: str = Field(
        min_length=2,
        max_length=100,
    )

    entity_type: str | None = Field(
        default=None,
        max_length=100,
    )

    entity_id: int | None = None

    description: str | None = None


class AdminActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int
    action: str
    entity_type: str | None
    entity_id: int | None
    description: str | None
    ip_address: str | None
    created_at: datetime