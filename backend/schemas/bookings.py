from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BookingResponse(BaseModel):
    """
    Response returned after successfully creating a flight booking.
    """

    id: int
    flight_order_id: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class UserBookingResponse(BaseModel):
    """
    Booking information returned when fetching a user's bookings.
    """

    id: int
    pnr: str | None = None
    status: str
    created_at: datetime | None = None
    ticket_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BookingCancellationResponse(BaseModel):
    """
    Response returned after cancelling a booking.
    """

    id: int
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class CursorPaginatedUserBookingResponse(BaseModel):
    """
    Cursor-paginated response for user bookings.
    """

    items: list[UserBookingResponse]

    next_cursor: str | None = None
    has_more: bool = False
    has_previous: bool = False
    total_count: int | None = None
    limit: int

    model_config = ConfigDict(from_attributes=True)
