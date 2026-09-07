
from datetime import date, datetime

from sqlalchemy import (
    String,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    builder_id: Mapped[int] = mapped_column(
        ForeignKey("builders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    project_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    price_from: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    price_to: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    total_units: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    total_towers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    possession_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    state_id: Mapped[int | None] = mapped_column(
        ForeignKey("states.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    locality_id: Mapped[int | None] = mapped_column(
        ForeignKey("localities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    landmark: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    rera_number: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ProjectUnit(Base):
    __tablename__ = "project_units"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    configuration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    bedrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    bathrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    area_unit: Mapped[str] = mapped_column(
        String(20),
        default="SQFT",
        nullable=False,
    )

    price_from: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    price_to: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    total_units: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    available_units: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )