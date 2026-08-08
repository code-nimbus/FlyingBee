from typing import Any, Literal, Optional

from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from sqlmodel import SQLModel


class FlightResponse(SQLModel):
    flight_number: str | None = None
    airline: str | None = None

    origin: str
    destination: str

    departure_at: str

    duration: int = 0
    transfers: int = 0

    gate: str | None = None
    booking_link: str | None = None

    price: float = 0


class FlightSearch(SQLModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)

    departure_date: str
    return_date: Optional[str] = None

    adults: int = Field(default=1, ge=1, le=9)
    children: int = Field(default=0, ge=0, le=8)
    infants: int = Field(default=0, ge=0, le=8)

    cabin_class: Literal[
        "economy",
        "premium_economy",
        "business",
        "first",
    ] = "economy"

    currency: Literal[
        "USD",
        "INR",
        "EUR",
        "GBP",
    ] = "USD"

    direct_only: bool = False

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    sort_by: Literal[
        "price",
        "duration",
        "departure",
    ] = "price"

    @field_validator("origin", "destination")
    @classmethod
    def airport_code(cls, value: str):
        value = value.upper()

        if len(value) != 3:
            raise ValueError("Airport code must be exactly 3 letters")

        return value

    @field_validator("departure_date")
    @classmethod
    def departure_date_validation(cls, value: str):
        datetime.strptime(
            value,
            "%Y-%m-%d",
        )

        return value

    @field_validator("return_date")
    @classmethod
    def return_date_validation(cls, value: str | None):
        if value is None:
            return value

        datetime.strptime(
            value,
            "%Y-%m-%d",
        )

        return value


class FlightSearchResponse(SQLModel):
    success: bool
    currency: str
    count: int
    flights: list[FlightResponse]


# --------------------------------------------------
# Flight Offer
# --------------------------------------------------
#
# This follows the same role as Nehemiah's FlightOffer.
# It represents a selected flight that can be sent to
# /shopping/flight-offers/pricing.
#
# TravelPayouts does NOT require this exact structure.
# We are keeping the structure because we want the
# application/router naming to stay close to Nehemiah.
# --------------------------------------------------


class FlightOffer(BaseModel):
    flight_number: str | None = None
    airline: str | None = None

    origin: str
    destination: str

    departure_at: str | None = None

    duration: Any | None = None
    transfers: int = 0

    gate: str | None = None
    booking_link: str | None = None

    price: float | None = None
    currency: str | None = None
