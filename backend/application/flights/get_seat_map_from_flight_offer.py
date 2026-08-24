from collections.abc import Mapping
from typing import Any, Protocol

SeatMapResult = list[dict[str, Any]]


class SeatMapFromOfferError(Exception):
    """Base exception for seat-map-from-flight-offer operations."""


class InvalidSeatMapOfferRequest(SeatMapFromOfferError):
    """Raised when the flight offer is invalid."""


class SeatMapFromOfferProviderError(SeatMapFromOfferError):
    """Raised when the external seat-map provider fails."""


class SeatMapFromOfferProvider(Protocol):
    def view_seat_map_for_offer(
        self,
        flight_offer: dict[str, Any],
    ) -> SeatMapResult: ...


class GetSeatMapFromFlightOffer:
    def __init__(
        self,
        *,
        seat_map_provider: SeatMapFromOfferProvider,
    ):
        self.seat_map_provider = seat_map_provider

    def execute(
        self,
        flight_offer: Mapping[str, Any],
    ) -> SeatMapResult:
        """
        Retrieve a seat map directly from a flight offer.

        The flight offer is converted to a regular dictionary before
        being passed to the infrastructure/provider layer.
        """

        if not flight_offer:
            raise InvalidSeatMapOfferRequest("Flight offer is required")

        try:
            return self.seat_map_provider.view_seat_map_for_offer(dict(flight_offer))

        except SeatMapFromOfferError:
            raise

        except Exception as exc:
            raise SeatMapFromOfferProviderError(
                "Failed to retrieve seat map from flight offer"
            ) from exc
