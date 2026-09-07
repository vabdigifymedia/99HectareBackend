
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionPlanCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    duration_days: int

    max_listings: int = 0
    max_inquiries: int = 0
    max_saved_searches: int = 0

    featured_listing_allowed: bool = False
    priority_support: bool = False


class SubscriptionPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    duration_days: int | None = None

    max_listings: int | None = None
    max_inquiries: int | None = None
    max_saved_searches: int | None = None

    featured_listing_allowed: bool | None = None
    priority_support: bool | None = None

    is_active: bool | None = None


class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    duration_days: int

    max_listings: int
    max_inquiries: int
    max_saved_searches: int

    featured_listing_allowed: bool
    priority_support: bool

    is_active: bool

    created_at: datetime
    updated_at: datetime


class UserSubscriptionCreate(BaseModel):
    plan_id: int
    auto_renew: bool = False


class UserSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    plan_id: int

    start_date: datetime
    end_date: datetime

    status: str
    auto_renew: bool

    remaining_inquiries: int
    remaining_listings: int

    created_at: datetime
    updated_at: datetime