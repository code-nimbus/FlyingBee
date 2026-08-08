import uuid
from datetime import date, datetime

from sqlmodel import Field, Relationship, SQLModel


class FlightOrder(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    user_id: uuid.UUID = Field(
        foreign_key="userindb.id",
        index=True,
    )

    flight_number: str | None = None
    airline: str | None = None

    origin: str
    destination: str

    departure_at: str

    price: float
    currency: str

    booking_link: str | None = None

    status: str = "CREATED"

    created_at: datetime = Field(default_factory=datetime.utcnow)

    travelers: list["Traveler"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
        },
    )


class Traveler(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    order_id: uuid.UUID = Field(foreign_key="flightorder.id")

    first_name: str
    last_name: str

    date_of_birth: date

    gender: str

    email: str
    phone: str

    passport_number: str | None = None
    passport_expiry: date | None = None
    passport_country: str | None = None

    order: FlightOrder = Relationship(
        back_populates="travelers",
    )
