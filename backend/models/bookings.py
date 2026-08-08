import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from backend.models.orders import FlightOrder


class Booking(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    user_id: uuid.UUID = Field(
        foreign_key="userindb.id",
        index=True,
    )

    flight_order_id: uuid.UUID = Field(
        foreign_key="flightorder.id",
        unique=True,
    )

    status: str = "CONFIRMED"

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    flight_order: "FlightOrder" = Relationship()
