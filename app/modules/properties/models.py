import re
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    property_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    listing_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        default="DRAFT",
        nullable=False,
        index=True,
    )

    price: Mapped[float] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    price_per_sqft: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    maintenance_charge: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    security_deposit: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    booking_amount: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    is_price_negotiable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    carpet_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    built_up_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    super_built_up_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    plot_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    area_unit: Mapped[str] = mapped_column(
        String(20),
        default="SQFT",
        nullable=False,
    )

    bedrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    bathrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    balconies: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    floor_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    total_floors: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    furnishing_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    facing: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    parking_spaces: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    property_age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    year_built: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    construction_status: Mapped[str | None] = mapped_column(
        String(40),
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

    sub_locality_id: Mapped[int | None] = mapped_column(
        ForeignKey("sub_localities.id", ondelete="SET NULL"),
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
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    builder_id: Mapped[int | None] = mapped_column(
        ForeignKey("builders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    rera_number: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    ownership_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    owner = relationship(
        "User",
        back_populates="properties",
        foreign_keys=[owner_id],
    )

    agent = relationship(
        "Agent",
        back_populates="properties",
        foreign_keys=[agent_id],
    )

    builder = relationship(
        "Builder",
        back_populates="properties",
        foreign_keys=[builder_id],
    )

    project = relationship(
        "Project",
        back_populates="properties",
        foreign_keys=[project_id],
    )

    country = relationship("Country")
    state = relationship("State")
    city = relationship("City")
    locality = relationship("Locality")
    sub_locality = relationship("SubLocality")

    media = relationship(
        "PropertyMedia",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    documents = relationship(
        "PropertyDocument",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    amenities = relationship(
        "Amenity",
        secondary="property_amenities",
        back_populates="properties",
    )

    residential_details = relationship(
        "ResidentialPropertyDetails",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )

    commercial_details = relationship(
        "CommercialPropertyDetails",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )

    plot_details = relationship(
        "PlotPropertyDetails",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )

    inquiries = relationship(
        "Inquiry",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    visits = relationship(
        "Visit",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    favorites = relationship(
        "Favorite",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    @property
    def slug(self) -> str:
        s = re.sub(r"[^a-zA-Z0-9]+", "-", self.title or "").strip("-").lower()
        return f"{s}-{self.id}" if s else f"property-{self.id}"


class ResidentialPropertyDetails(Base):
    __tablename__ = "residential_property_details"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    servant_room: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    study_room: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    pooja_room: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    store_room: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    other_room: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    electricity_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    water_supply: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    gas_pipeline: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    property = relationship(
        "Property",
        back_populates="residential_details",
    )


class CommercialPropertyDetails(Base):
    __tablename__ = "commercial_property_details"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    commercial_sub_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    washrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    conference_rooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    cabins: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    pantry: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    reception_area: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    power_backup: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    property = relationship(
        "Property",
        back_populates="commercial_details",
    )


class PlotPropertyDetails(Base):
    __tablename__ = "plot_property_details"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    plot_length: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    plot_width: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    road_width: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    boundary_wall: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    corner_plot: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    gated_community: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    property = relationship(
        "Property",
        back_populates="plot_details",
    )