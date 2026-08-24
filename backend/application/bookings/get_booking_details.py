from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


@dataclass(frozen=True)
class BookingDetailsRecord:
    """
    Represents the booking information required to retrieve
    and present booking details.
    """

    id: UUID
    created_at: datetime
    status: str
    flight_order_response: dict[str, Any] | None
    ticket_url: str | None


class BookingDetailsError(Exception):
    """Base exception for booking-details operations."""


class BookingDetailsNotFound(BookingDetailsError):
    """Raised when the booking does not exist or does not belong to the user."""


class BookingDetailsRepository(Protocol):
    """
    Repository interface required by the booking-details use case.
    """

    def get_user_booking_details(
        self,
        *,
        booking_id: UUID,
        user_id: UUID,
    ) -> BookingDetailsRecord | None: ...


class BookingDetailsPresenter(Protocol):
    """
    Presenter interface used to transform booking data
    into the API response format.
    """

    def present(
        self,
        *,
        booking: BookingDetailsRecord,
        user_email: str,
    ) -> dict[str, Any]: ...


class GetBookingDetails:
    """
    Application use case for retrieving booking details
    for an authenticated user.
    """

    def __init__(
        self,
        *,
        booking_repository: BookingDetailsRepository,
        presenter: BookingDetailsPresenter,
    ):
        self.booking_repository = booking_repository
        self.presenter = presenter

    def execute(
        self,
        *,
        booking_id: UUID,
        user_id: UUID,
        user_email: str,
    ) -> dict[str, Any]:
        booking = self.booking_repository.get_user_booking_details(
            booking_id=booking_id,
            user_id=user_id,
        )

        if booking is None:
            raise BookingDetailsNotFound

        return self.presenter.present(
            booking=booking,
            user_email=user_email,
        )
