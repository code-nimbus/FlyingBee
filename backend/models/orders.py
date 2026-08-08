import uuid

from datetime import datetime

from sqlmodel import SQLModel, Field


class FlightOrder(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    flight_number: str

    airline: str

    origin: str

    destination: str

    departure_at: str

    price: float

    currency: str

    booking_link: str | None = None

    status: str = "CREATED"

    created_at: datetime = Field(default_factory=datetime.utcnow)
