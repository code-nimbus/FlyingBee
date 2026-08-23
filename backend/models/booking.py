from datetime import datetime, timezone
from typing import Optional

from uuid import UUID
from sqlmodel import Field, SQLModel


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: UUID

    flight_order_id: str = Field(
        index=True,
        unique=True,
    )

    status: str = Field(
        default="confirmed",
        index=True,
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
