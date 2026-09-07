
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ReviewCreate(BaseModel):
    agent_id: int | None = None

    builder_id: int | None = None

    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReviewUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReviewModerationUpdate(BaseModel):
    is_verified: bool | None = None

    is_published: bool | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    agent_id: int | None
    builder_id: int | None

    rating: int
    comment: str | None

    is_verified: bool
    is_published: bool

    created_at: datetime
    updated_at: datetime


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    page_size: int