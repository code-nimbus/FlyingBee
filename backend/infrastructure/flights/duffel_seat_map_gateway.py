from typing import Any

from backend.application.bookings.get_seat_map import (
    InvalidSeatMapRequest,
    SeatMapProviderError,
)
from backend.application.flights.get_seat_map_from_flight_offer import (
    InvalidSeatMapOfferRequest,
    SeatMapFromOfferProviderError,
)
from backend.external_services.interface import FlightServiceProtocol


class DuffelSeatMapGateway:
    def __init__(self, flight_service: FlightServiceProtocol):
        self.flight_service = flight_service

    def view_seat_map(
        self,
        *,
        offer_id: str,
    ) -> list[dict[str, Any]]:
        try:
            return self.flight_service.view_seat_map_get(offer_id)

        except ValueError as exc:
            raise InvalidSeatMapRequest(str(exc)) from exc

        except Exception as exc:
            raise SeatMapProviderError("Duffel seat map request failed") from exc

    def view_seat_map_for_offer(
        self,
        flight_offer: dict[str, Any],
    ) -> list[dict[str, Any]]:
        try:
            return self.flight_service.view_seat_map_post(flight_offer)

        except ValueError as exc:
            raise InvalidSeatMapOfferRequest(str(exc)) from exc

        except Exception as exc:
            raise SeatMapFromOfferProviderError from exc
