from typing import Any, Protocol


class FlightServiceProtocol(Protocol):
    def search_flights(
        self,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Search flights using the configured flight provider.

        The request body is provider-specific.
        For Duffel, this contains:

        {
            "data": {
                "slices": [...],
                "passengers": [...],
                "cabin_class": "economy"
            }
        }
        """
        ...

    def confirm_price(
        self,
        offer_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve/confirm the current price of a flight offer.
        """
        ...

    def create_flight_order(
        self,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create a flight order from a selected flight offer.
        """
        ...

    def search_flights_get(
        self,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Search flights using GET-style/provider-specific parameters.

        Kept for compatibility with other flight providers or
        existing application code.
        """
        ...

    def view_seat_map_get(
        self,
        offer_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve the seat map for a flight offer.
        """
        ...

    def view_seat_map_post(
        self,
        flight_offer: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Retrieve the seat map using a flight-offer payload.
        """
        ...

    def get_flight_order(
        self,
        flight_orderId: str,
    ) -> dict[str, Any]:
        """
        Retrieve an existing flight order.
        """
        ...

    def cancel_flight_order(
        self,
        flight_orderId: str,
    ) -> dict[str, Any]:
        """
        Cancel an existing flight order.
        """
        ...

    def airport_city_search(
        self,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Search airports/cities/places.
        """
        ...

    def get_flight_orders(
        self,
        flight_order_ids: list[str],
    ) -> list[dict[str, Any]]:
        """
        Retrieve multiple flight orders.
        """
        ...
