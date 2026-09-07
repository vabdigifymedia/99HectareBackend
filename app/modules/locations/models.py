
from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Float,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    iso_code: Mapped[str | None] = mapped_column(
        String(10),
        unique=True,
        nullable=True,
    )

    phone_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    state_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    state_id: Mapped[int] = mapped_column(
        ForeignKey("states.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class Locality(Base):
    __tablename__ = "localities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class SubLocality(Base):
    __tablename__ = "sub_localities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    locality_id: Mapped[int] = mapped_column(
        ForeignKey("localities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )