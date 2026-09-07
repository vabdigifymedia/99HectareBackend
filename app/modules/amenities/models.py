
# app/modules/amenities/models.py

from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


property_amenities = Table(
    "property_amenities",
    Base.metadata,

    Column(
        "property_id",
        ForeignKey("properties.id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "amenity_id",
        ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


project_amenities = Table(
    "project_amenities",
    Base.metadata,

    Column(
        "project_id",
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "amenity_id",
        ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Amenity(Base):
    __tablename__ = "amenities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    icon: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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