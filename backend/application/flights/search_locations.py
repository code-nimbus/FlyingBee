import json
from collections.abc import Mapping
from typing import Any, Protocol

LocationSearchResult = list[dict[str, Any]]


class LocationSearchError(Exception):
    """Base exception for location search errors."""


class InvalidLocationSearchRequest(LocationSearchError):
    """Raised when the location search request is invalid."""


class LocationSearchProviderError(LocationSearchError):
    """Raised when the location search provider fails."""


class LocationSearchCache(Protocol):
    """Interface for caching location search results."""

    def get(self, key: str) -> LocationSearchResult | None: ...

    def set(self, key: str, value: LocationSearchResult) -> None: ...


class LocationSearchProvider(Protocol):
    """Interface for a location search provider."""

    def search(
        self,
        criteria: dict[str, Any],
    ) -> LocationSearchResult: ...


class SearchLocations:
    """Use case for searching airports and cities."""

    def __init__(
        self,
        provider: LocationSearchProvider,
        cache: LocationSearchCache,
    ):
        self.provider = provider
        self.cache = cache

    def execute(
        self,
        criteria: Mapping[str, Any],
    ) -> LocationSearchResult:
        request_body = dict(criteria)
        cache_key = self._build_cache_key(request_body)

        cached_response = self.cache.get(cache_key)

        if cached_response is not None:
            return cached_response

        response = self.provider.search(request_body)

        self.cache.set(cache_key, response)

        return response

    @staticmethod
    def _build_cache_key(
        data: Mapping[str, Any],
    ) -> str:
        normalized = json.dumps(
            dict(data),
            sort_keys=True,
            separators=(",", ":"),
        )

        return f"location_search:{normalized}"
