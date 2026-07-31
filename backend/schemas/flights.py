from typing import Literal, Optional

from pydantic import Field, field_validator
from sqlmodel import SQLModel
from datetime import datetime


class FlightSearch(SQLModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)

    departure_date: str
    return_date: Optional[str] = None

    adults: int = Field(default=1, ge=1, le=9)
    children: int = Field(default=0, ge=0, le=8)
    infants: int = Field(default=0, ge=0, le=8)

    cabin_class: Literal["economy", "premium_economy", "business", "first"] = "economy"

    currency: Literal["USD", "INR", "EUR", "GBP"] = "USD"

    direct_only: bool = False

    limit: int = Field(default=20, ge=1, le=100)

    sort_by: Literal["price", "duration", "departure"] = "price"

    @field_validator("origin", "destination")
    @classmethod
    def airport_code(cls, value):
        value = value.upper()

        if len(value) != 3:
            raise ValueError("Airport code must be exactly 3 letters")

        return value

    @field_validator("departure_date")
    @classmethod
    def departure_date_validation(cls, value):
        datetime.strptime(value, "%Y-%m-%d")
        return value

    @field_validator("return_date")
    @classmethod
    def return_date_validation(cls, value):
        if value is None:
            return value

        datetime.strptime(value, "%Y-%m-%d")
        return value


class FlightResponse(SQLModel):
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure_at: str
    duration: int
    transfers: int
    gate: str
    booking_link: str
    price: float
