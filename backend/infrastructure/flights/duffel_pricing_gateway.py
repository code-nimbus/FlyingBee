import logging
from typing import Any

from backend.application.flights.confirm_flight_price import (
    FlightPricingProviderError,
    FlightPricingResult,
    InvalidFlightPricingRequest,
)
from backend.external_services.interface import FlightServiceProtocol

logger = logging.getLogger(__name__)


class DuffelPricingGateway:
    def __init__(self, flight_service: FlightServiceProtocol):
        self.flight_service = flight_service

    def confirm_price(
        self,
        flight_offer: dict[str, Any],
    ) -> FlightPricingResult:
        try:
            offer_id = flight_offer.get("id")
            if not offer_id:
                raise ValueError("Flight offer id is required")
            return self.flight_service.confirm_price(offer_id)

        except ValueError as exc:
            logger.exception("Invalid flight pricing request")
            raise InvalidFlightPricingRequest from exc

        except Exception as exc:
            logger.exception("Duffel flight pricing failed")
            raise FlightPricingProviderError from exc
