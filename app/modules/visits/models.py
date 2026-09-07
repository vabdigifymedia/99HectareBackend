
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    requested_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    confirmed_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="REQUESTED",
        index=True
    )

    user_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    agent_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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
        back_populates="visits"
    )

    property = relationship(
        "Property",
        back_populates="visits"
    )

    agent = relationship(
        "Agent",
        back_populates="visits"
    )