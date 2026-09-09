from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
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

    property_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    listing_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    min_price: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    max_price: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    min_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    max_area: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    bedrooms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    furnishing_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    filters: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    notify_new_listings: Mapped[bool] = mapped_column(
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
        back_populates="saved_searches",
    )

    city = relationship("City")
    locality = relationship("Locality")