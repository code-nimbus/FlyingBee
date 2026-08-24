from collections.abc import Mapping
from typing import Any, Protocol

FlightPricingResult = Any


class FlightPricingError(Exception):
    """Base exception for flight pricing errors."""


class InvalidFlightPricingRequest(FlightPricingError):
    """Raised when the flight pricing request is invalid."""


class FlightPricingProviderError(FlightPricingError):
    """Raised when the flight pricing provider fails."""


class FlightPricingProvider(Protocol):
    """Interface for a flight pricing provider."""

    def confirm_price(
        self,
        flight_offer: dict[str, Any],
    ) -> FlightPricingResult: ...


class ConfirmFlightPrice:
    """Use case for confirming the price of a flight offer."""

    def __init__(self, provider: FlightPricingProvider):
        self.provider = provider

    def execute(
        self,
        flight_offer: Mapping[str, Any],
    ) -> FlightPricingResult:
        return self.provider.confirm_price(dict(flight_offer))
