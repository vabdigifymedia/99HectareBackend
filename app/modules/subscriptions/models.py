
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("subscription_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
        index=True
    )

    auto_renew: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    remaining_inquiries: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    remaining_listings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="subscriptions"
    )

    plan = relationship(
        "SubscriptionPlan",
        back_populates="subscriptions"
    )

    payments = relationship(
        "Payment",
        back_populates="subscription"
    )


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    duration_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    max_listings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    max_inquiries: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    max_saved_searches: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    featured_listing_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    priority_support: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    subscriptions = relationship(
        "UserSubscription",
        back_populates="plan"
    )