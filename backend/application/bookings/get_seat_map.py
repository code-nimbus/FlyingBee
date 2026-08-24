from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID


@dataclass(frozen=True)
class SeatMapBookingRecord:
    id: UUID
    user_id: UUID
    flight_order_id: str


class SeatMapError(Exception):
    """Base exception for seat-map operations."""


class SeatMapBookingNotFound(SeatMapError):
    """Raised when the booking does not exist or does not belong to the user."""


class InvalidSeatMapRequest(SeatMapError):
    """Raised when the seat-map request is invalid."""


class SeatMapProviderError(SeatMapError):
    """Raised when the external seat-map provider fails."""


class SeatMapBookingRepository(Protocol):
    def get_user_booking_for_seat_map(
        self, *, booking_id: UUID, user_id: UUID
    ) -> SeatMapBookingRecord | None: ...


class SeatMapProvider(Protocol):
    def view_seat_map(
        self,
        *,
        flight_order_id: str,
    ) -> list[dict[str, Any]]: ...


class GetSeatMap:
    def __init__(
        self,
        *,
        booking_repository: SeatMapBookingRepository,
        seat_map_provider: SeatMapProvider,
    ):
        self.booking_repository = booking_repository
        self.seat_map_provider = seat_map_provider

    def execute(
        self, *, flight_order_reference: str, user_id: UUID
    ) -> list[dict[str, Any]]:
        try:
            booking_id = UUID(flight_order_reference)
        except ValueError:
            return self.seat_map_provider.view_seat_map(
                flight_order_id=flight_order_reference
            )
        """
        Retrieve a seat map.

        flight_order_reference can be either:
        1. Our internal booking UUID
        2. A Duffel flight order ID

        If it is a UUID, we verify that the booking belongs
        to the authenticated user before requesting the seat map.

        If it is not a UUID, we treat it directly as the
        external Duffel flight order ID.
        """

        booking = self.booking_repository.get_by_id(
            booking_id=booking_id,
            user_id=user_id,
        )

        if booking is None:
            raise SeatMapBookingNotFound

        if not booking.offer_id:
            raise InvalidSeatMapRequest("Booking does not have an associated offer")

        return self.seat_map_provider.view_seat_map(
            flight_order_id=booking.flight_order_id
        )
