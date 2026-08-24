from typing import Any

from backend.application.bookings.get_booking_details import (
    BookingDetailsRecord,
)
from backend.utils.booking_transformer import (
    transform_duffel_order_to_booking_success,
)


class BookingSuccessPresenter:
    """
    Presenter for converting a stored Duffel booking into the
    frontend-friendly booking success/details response.
    """

    def present(
        self,
        *,
        booking: BookingDetailsRecord,
        user_email: str,
    ) -> dict[str, Any]:
        return transform_duffel_order_to_booking_success(
            booking_id=str(booking.id),
            booking_date=booking.created_at,
            booking_status=booking.status,
            flight_order_id=booking.flight_order_id,
            duffel_order=booking.duffel_order_response or {},
            user_email=user_email,
        )
