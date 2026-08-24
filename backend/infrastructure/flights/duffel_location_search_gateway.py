from typing import Any

import requests
from backend.application.flights.search_locations import (
    InvalidLocationSearchRequest,
    LocationSearchProviderError,
    LocationSearchResult,
)
from backend.external_services.interface import FlightServiceProtocol


class DuffelLocationSearchGateway:
    def __init__(self, flight_service: FlightServiceProtocol):
        self.flight_service = flight_service

    def search_locations(
        self,
        criteria: dict[str, Any],
    ) -> LocationSearchResult:
        try:
            return self.flight_service.airport_city_search(criteria)

        except ValueError as exc:
            raise InvalidLocationSearchRequest from exc

        except requests.exceptions.RequestException as exc:
            raise LocationSearchProviderError from exc
