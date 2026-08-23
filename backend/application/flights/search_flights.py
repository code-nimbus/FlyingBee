import json
from collections.abc import Mapping
from typing import Any, Protocol


FlightSearchResult = list[dict[str, Any]]


class FlightSearchError(Exception):
    pass


class InvalidFlightSearchRequest(FlightSearchError):
    pass


class FlightSearchProviderError(FlightSearchError):
    pass


class FlightSearchCache(Protocol):
    def get(self, key: str) -> FlightSearchResult | None: ...

    def set(self, key: str, value: FlightSearchResult) -> None: ...


class FlightSearchProvider(Protocol):
    def search(self, criteria: dict[str, Any]) -> FlightSearchResult: ...


class SearchFlights:
    def __init__(
        self,
        provider: FlightSearchProvider,
        cache: FlightSearchCache,
    ):
        self.provider = provider
        self.cache = cache

    def execute(
        self,
        criteria: Mapping[str, Any],
    ) -> FlightSearchResult:
        request_body = dict(criteria)

        self._validate_request(request_body)

        cache_key = self._build_cache_key(request_body)

        cached_response = self.cache.get(cache_key)

        if cached_response is not None:
            return cached_response

        response = self.provider.search(request_body)

        self.cache.set(cache_key, response)

        return response

    @staticmethod
    def _validate_request(
        data: Mapping[str, Any],
    ) -> None:
        origin = data.get("originLocationCode")
        destination = data.get("destinationLocationCode")
        departure_date = data.get("departureDate")

        if not origin:
            raise InvalidFlightSearchRequest("originLocationCode is required")

        if not destination:
            raise InvalidFlightSearchRequest("destinationLocationCode is required")

        if not departure_date:
            raise InvalidFlightSearchRequest("departureDate is required")

        if origin.upper() == destination.upper():
            raise InvalidFlightSearchRequest(
                "Origin and destination cannot be the same"
            )

        adults = data.get("adults", 1)

        if adults < 1:
            raise InvalidFlightSearchRequest("At least one adult is required")

        children = data.get("children")

        if children is not None and children < 0:
            raise InvalidFlightSearchRequest("Children cannot be negative")

        infants = data.get("infants")

        if infants is not None and infants < 0:
            raise InvalidFlightSearchRequest("Infants cannot be negative")

        max_results = data.get("max", 5)

        if max_results < 1:
            raise InvalidFlightSearchRequest("max must be greater than 0")

    @staticmethod
    def _build_cache_key(
        data: Mapping[str, Any],
    ) -> str:
        normalized = json.dumps(
            dict(data),
            sort_keys=True,
            separators=(",", ":"),
        )

        return f"flight_search:{normalized}"
