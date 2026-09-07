
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class NotificationCreate(BaseModel):
    user_id: int

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    message: str

    notification_type: str = Field(
        min_length=2,
        max_length=50,
    )

    action_url: str | None = None


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    action_url: str | None
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int