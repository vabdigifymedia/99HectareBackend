
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    property_id: int


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    property_id: int
    created_at: datetime


class FavoriteListResponse(BaseModel):
    items: list[FavoriteResponse]
    total: int
    page: int
    page_size: int