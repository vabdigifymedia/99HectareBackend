from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="buyer",
        server_default="buyer",
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Profiles
    agent_profile = relationship(
        "Agent",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    builder_profile = relationship(
        "Builder",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    admin_profile = relationship(
        "Admin",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Relationships
    properties = relationship(
        "Property",
        back_populates="owner",
        foreign_keys="Property.owner_id",
    )

    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    saved_searches = relationship(
        "SavedSearch",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    inquiries = relationship(
        "Inquiry",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    visits = relationship(
        "Visit",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    subscriptions = relationship(
        "UserSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    reviews = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="reporter",
        foreign_keys="Report.reporter_id",
        cascade="all, delete-orphan",
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    otp_verifications = relationship(
        "OTPVerification",
        back_populates="user",
        cascade="all, delete-orphan",
    )