from sqlmodel import SQLModel
from typing import Optional


class FlightOrderRequest(SQLModel):
    flight_number: str

    airline: str

    origin: str

    destination: str

    departure_at: str

    price: float

    currency: str = "USD"

    booking_link: Optional[str] = None


class FlightOrderResponse(SQLModel):
    order_id: str

    status: str

    message: str
