from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Builder(Base):
    __tablename__ = "builders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    logo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    license_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    rera_registration_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False,
        index=True,
    )

    verification_document: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    established_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    # Relationships
    user = relationship(
        "User",
        back_populates="builder_profile",
    )

    projects = relationship(
        "Project",
        back_populates="builder",
        cascade="all, delete-orphan",
    )

    properties = relationship(
        "Property",
        back_populates="builder",
    )

    inquiries = relationship(
        "Inquiry",
        back_populates="builder",
    )

    reviews = relationship(
        "Review",
        back_populates="builder",
    )