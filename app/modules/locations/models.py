from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    states = relationship(
        "State",
        back_populates="country",
        cascade="all, delete-orphan",
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
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    country = relationship(
        "Country",
        back_populates="states",
    )

    cities = relationship(
        "City",
        back_populates="state",
        cascade="all, delete-orphan",
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
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    state = relationship(
        "State",
        back_populates="cities",
    )

    localities = relationship(
        "Locality",
        back_populates="city",
        cascade="all, delete-orphan",
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
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    city = relationship(
        "City",
        back_populates="localities",
    )

    sub_localities = relationship(
        "SubLocality",
        back_populates="locality",
        cascade="all, delete-orphan",
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
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    locality = relationship(
        "Locality",
        back_populates="sub_localities",
    )