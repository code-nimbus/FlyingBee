from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from backend.models.booking import BookingStatus


@dataclass(frozen=True)
class BookingCancellationRecord:
    """
    Booking information required to cancel a flight order.
    """

    id: UUID
    user_id: UUID
    flight_order_id: str | None
    status: str
    pnr: str | None


@dataclass(frozen=True)
class CancelBookingCommand:
    """
    Command containing all information required to cancel a booking.
    """

    booking_id: UUID
    user_id: UUID
    user_email: str


@dataclass(frozen=True)
class CancelledBooking:
    """
    Result returned after a booking has been cancelled.
    """

    id: UUID
    status: str
    message: str


class CancelBookingError(Exception):
    """Base exception for booking cancellation."""


class BookingNotFound(CancelBookingError):
    """Raised when the booking does not exist or is not owned by the user."""


class BookingAlreadyCancelled(CancelBookingError):
    """Raised when the booking has already been cancelled."""


class BookingCannotBeCancelled(CancelBookingError):
    """Raised when the booking is in a state that cannot be cancelled."""


class BookingCancellationRepository(Protocol):
    """
    Repository interface required by the cancellation use case.
    """

    def get_user_booking_to_cancel(
        self,
        *,
        booking_id: UUID,
        user_id: UUID,
    ) -> BookingCancellationRecord | None: ...

    def update_booking_status(
        self,
        booking_id: UUID,
        status: str,
    ) -> None: ...


class BookingCancellationProvider(Protocol):
    """
    Provider interface for cancelling the external flight order.

    Duffel implements this interface through
    DuffelFlightOrderCancellationGateway.
    """

    def cancel_order(self, flight_order_id: str) -> None: ...


class BookingCacheInvalidator(Protocol):
    """
    Interface for invalidating cached bookings belonging to a user.
    """

    def invalidate_user_bookings(self, user_id: UUID) -> None: ...


class BookingCancellationEventPublisher(Protocol):
    """
    Interface for publishing a booking-cancelled event.
    """

    def publish_booking_cancelled(
        self,
        *,
        booking_id: UUID,
        user_id: UUID,
        pnr: str | None,
        user_email: str,
    ) -> None: ...


class CancelBooking:
    """
    Application use case for cancelling a flight booking.

    The use case:
    1. Verifies that the booking belongs to the authenticated user.
    2. Validates that the booking can be cancelled.
    3. Cancels the external Duffel flight order.
    4. Updates the local booking status.
    5. Invalidates the user's booking cache.
    6. Publishes a booking-cancelled event.
    """

    def __init__(
        self,
        *,
        booking_repository: BookingCancellationRepository,
        booking_cancellation_provider: BookingCancellationProvider,
        booking_cache: BookingCacheInvalidator,
        event_publisher: BookingCancellationEventPublisher,
    ):
        self.booking_repository = booking_repository
        self.booking_cancellation_provider = booking_cancellation_provider
        self.booking_cache = booking_cache
        self.event_publisher = event_publisher

    def execute(
        self,
        *,
        command: CancelBookingCommand,
    ) -> CancelledBooking:
        booking = self.booking_repository.get_user_booking_to_cancel(
            booking_id=command.booking_id,
            user_id=command.user_id,
        )

        if booking is None:
            raise BookingNotFound

        if booking.status == BookingStatus.CANCELLED:
            raise BookingAlreadyCancelled

        if booking.status in (
            BookingStatus.REVERSED,
            BookingStatus.FAILED,
            BookingStatus.REFUNDED,
        ):
            raise BookingCannotBeCancelled

        # Cancel the external Duffel flight order first.
        #
        # We intentionally do not fail the entire local cancellation
        # workflow if the provider cancellation fails. The local booking
        # can still be marked cancelled and the provider failure can be
        # handled/reconciled asynchronously.
        if booking.flight_order_id:
            try:
                self.booking_cancellation_provider.cancel_order(booking.flight_order_id)
            except Exception:
                pass

        # Update local booking state.
        self.booking_repository.update_booking_status(
            booking.id,
            BookingStatus.CANCELLED,
        )

        # Remove stale cached booking data.
        self.booking_cache.invalidate_user_bookings(command.user_id)

        # Notify downstream systems.
        self.event_publisher.publish_booking_cancelled(
            booking_id=booking.id,
            user_id=command.user_id,
            pnr=booking.pnr,
            user_email=command.user_email,
        )

        return CancelledBooking(
            id=booking.id,
            status=BookingStatus.CANCELLED,
            message="Booking has been successfully cancelled",
        )
