
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PaymentCreate(BaseModel):
    subscription_id: int | None = None

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str = Field(
        default="INR",
        max_length=10,
    )

    payment_gateway: str = Field(
        min_length=2,
        max_length=50,
    )

    payment_method: str | None = Field(
        default=None,
        max_length=50,
    )


class PaymentUpdate(BaseModel):
    status: str = Field(
        pattern="^(PENDING|SUCCESS|FAILED|REFUNDED|CANCELLED)$"
    )

    gateway_payment_id: str | None = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    subscription_id: int | None
    amount: Decimal
    currency: str
    payment_gateway: str
    gateway_payment_id: str | None
    gateway_order_id: str | None
    status: str
    payment_method: str | None
    metadata: dict | None
    created_at: datetime
    updated_at: datetime