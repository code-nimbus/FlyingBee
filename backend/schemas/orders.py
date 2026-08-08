from datetime import date
from pydantic import BaseModel, EmailStr, Field


class Traveler(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

    date_of_birth: date

    gender: str = Field(min_length=1, max_length=20)

    email: EmailStr

    phone: str = Field(min_length=5, max_length=30)

    passport_number: str | None = Field(
        default=None,
        max_length=50,
    )

    passport_expiry: date | None = None

    passport_country: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )


class FlightOrderRequest(BaseModel):
    """
    Request used to create a booking.

    Contains the selected flight and traveler information.
    """

    flight_number: str | None = None
    airline: str | None = None

    origin: str
    destination: str

    departure_at: str

    price: float
    currency: str

    booking_link: str | None = None

    travelers: list[Traveler] = Field(
        min_length=1,
        max_length=9,
    )


class FlightOrderResponse(BaseModel):
    order_id: str
    status: str
    message: str
    travelers_count: int
