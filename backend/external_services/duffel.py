import os
import requests
from dotenv import load_dotenv

from backend.utils.log_manager import get_app_logger

load_dotenv()

logger = get_app_logger(__name__)


class DuffelFlightService:
    def __init__(self):
        self.api_token = self.get_duffel_credentials()

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Duffel-Version": "v2",
        }

        self.base_url = "https://api.duffel.com"

    def get_duffel_credentials(self) -> str:
        api_token = os.getenv("DUFFEL_API_TOKEN")

        if not api_token:
            raise ValueError("Duffel API credentials not configured")

        return api_token

    def search_flights(self, request_body: dict) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/air/offer_requests",
                headers=self.headers,
                json=request_body,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as error:
            raise error

    def confirm_price(self, offer_id: str) -> dict:
        try:
            response = requests.get(
                f"{self.base_url}/air/offers/{offer_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as error:
            raise error

    # def create_flight_order(self, request_body: dict) -> dict:
    #     """
    #     Creates a flight order using a selected Duffel flight offer.

    #     IMPORTANT:
    #     The offer should be retrieved shortly before booking because
    #     Duffel offers expire and their price can change.
    #     """
    #     try:
    #         data = request_body.get("data")

    #         if not data:
    #             raise ValueError("data is required in request body")

    #         selected_offers = data.get("selected_offers")
    #         passengers = data.get("passengers")

    #         if not selected_offers:
    #             raise ValueError(
    #                 "selected_offers is required in request body"
    #             )

    #         if not passengers:
    #             raise ValueError(
    #                 "passengers information is required"
    #             )

    #         response = requests.post(
    #             f"{self.base_url}/air/orders",
    #             headers=self.headers,
    #             json=request_body,
    #         )
    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         raise error

    # def search_flights_get(self, request_body: dict) -> dict:
    #     try:
    #         response = requests.get(
    #             f"{self.base_url}/air/offer_requests",
    #             headers=self.headers,
    #             params=request_body,
    #         )
    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         raise error

    # def view_seat_map_get(self, offer_id: str) -> dict:
    #     try:
    #         response = requests.get(
    #             f"{self.base_url}/air/offers/{offer_id}/seat_maps",
    #             headers=self.headers,
    #         )
    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         raise error

    # def view_seat_map_post(self, flight_offer: dict) -> dict:
    #     try:
    #         offer_id = flight_offer.get("id")

    #         if not offer_id:
    #             raise ValueError("offer id is required")

    #         response = requests.get(
    #             f"{self.base_url}/air/offers/{offer_id}/seat_maps",
    #             headers=self.headers,
    #         )
    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         raise error

    # def get_flight_order(self, flight_orderId: str) -> dict:
    #     """
    #     Retrieves flight order details using the Duffel Orders API.

    #     Args:
    #         flight_orderId (str): The ID of the flight order.

    #     Returns:
    #         dict: The flight order details.
    #     """
    #     try:
    #         response = requests.get(
    #             f"{self.base_url}/air/orders/{flight_orderId}",
    #             headers=self.headers,
    #         )
    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         raise error

    # def create_flight_order(self, request_body: dict) -> dict:
    #     """
    #     Creates a flight order using a selected Duffel flight offer.
    #     """

    #     try:
    #         data = request_body.get("data")

    #         if not isinstance(data, dict):
    #             raise ValueError(
    #                 "data is required in request body"
    #             )

    #         selected_offers = data.get("selected_offers")
    #         passengers = data.get("passengers")
    #         order_type = data.get("type")

    #         if not selected_offers:
    #             raise ValueError(
    #                 "selected_offers is required"
    #             )

    #         if len(selected_offers) != 1:
    #             raise ValueError(
    #                 "Exactly one selected offer is required"
    #             )

    #         if not passengers:
    #             raise ValueError(
    #                 "passengers are required"
    #             )

    #         if order_type not in {"hold", "instant"}:
    #             raise ValueError(
    #                 "type must be 'hold' or 'instant'"
    #             )

    #         if order_type == "instant" and not data.get("payments"):
    #             raise ValueError(
    #                 "payments are required for instant orders"
    #             )

    #         if order_type == "hold" and data.get("payments"):
    #             raise ValueError(
    #                 "payments must not be provided for hold orders"
    #             )

    #         response = requests.post(
    #             f"{self.base_url}/air/orders",
    #             headers=self.headers,
    #             json=request_body,
    #             timeout=30,
    #         )

    #         response.raise_for_status()

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         raise error
    # def create_flight_order(self, request_body: dict) -> dict:
    #     """
    #     Creates a flight order using a selected Duffel flight offer.
    #     """
    #     data = request_body.get("data")

    #     if not isinstance(data, dict):
    #         raise ValueError("data is required in request body")

    #     selected_offers = data.get("selected_offers")
    #     passengers = data.get("passengers")
    #     order_type = data.get("type")

    #     if not selected_offers:
    #         raise ValueError("selected_offers is required")

    #     if len(selected_offers) != 1:
    #         raise ValueError("Exactly one selected offer is required")

    #     if not passengers:
    #         raise ValueError("passengers are required")

    #     if order_type not in {"hold", "instant"}:
    #         raise ValueError("type must be 'hold' or 'instant'")

    #     if order_type == "instant" and not data.get("payments"):
    #         raise ValueError("payments are required for instant orders")

    #     if order_type == "hold" and data.get("payments"):
    #         raise ValueError("payments must not be provided for hold orders")

    # #     response = requests.post(
    # #         f"{self.base_url}/air/orders",
    # #         headers=self.headers,
    # #         json=request_body,
    # #         timeout=30,
    # # )
    #     response = requests.post(
    #         f"{self.base_url}/air/orders",
    #         headers=self.headers,
    #         json=request_body,
    #         timeout=30,
    #     )

    #     if not response.ok:
    #         logger.error(
    #             "Duffel order creation failed: "
    #             "status=%s response=%s request=%s",
    #             response.status_code,
    #             response.text,
    #             request_body,
    #         )

    #     response.raise_for_status()

    #     return response.json()

    def create_flight_order(self, request_body: dict) -> dict:
        """
        Creates a flight order using a selected Duffel flight offer.
        """
        data = request_body.get("data")

        if not isinstance(data, dict):
            raise ValueError("data is required in request body")

        selected_offers = data.get("selected_offers")
        passengers = data.get("passengers")
        order_type = data.get("type")

        if not selected_offers:
            raise ValueError("selected_offers is required")

        if len(selected_offers) != 1:
            raise ValueError("Exactly one selected offer is required")

        if not passengers:
            raise ValueError("passengers are required")

        if order_type not in {"hold", "instant"}:
            raise ValueError("type must be 'hold' or 'instant'")

        if order_type == "instant" and not data.get("payments"):
            raise ValueError("payments are required for instant orders")

        if order_type == "hold" and "payments" in data:
            raise ValueError("payments must not be provided for hold orders")

        response = requests.post(
            f"{self.base_url}/air/orders",
            headers=self.headers,
            json=request_body,
            timeout=30,
        )

        if not response.ok:
            logger.error(
                "Duffel order creation failed | status=%s | response=%s",
                response.status_code,
                response.text,
            )

        response.raise_for_status()

        return response.json()

    def cancel_flight_order(self, flight_orderId: str) -> dict:
        """
        Cancels a flight order using the Duffel Order Cancellations API.

        Args:
            flight_orderId (str): The ID of the flight order.

        Returns:
            dict: The cancellation details.
        """
        try:
            request_body = {"data": {"order_id": flight_orderId}}

            response = requests.post(
                f"{self.base_url}/air/order_cancellations",
                headers=self.headers,
                json=request_body,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as error:
            raise error

    def airport_city_search(self, request_body: dict) -> dict:
        """
        Searches airports/places using Duffel's Places API.

        Args:
            request_body:
                {
                    "query": "London"
                }

        Returns:
            dict: Matching places.
        """
        try:
            keyword = request_body.get("keyword")

            if not keyword:
                raise ValueError("keyword is required")

            response = requests.get(
                f"{self.base_url}/places/suggestions",
                headers=self.headers,
                params={"query": keyword},
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as error:
            raise error

    def get_flight_orders(self, flight_order_ids: list[str]):
        """
        Retrieve multiple flight orders based on their IDs.
        """
        try:
            flight_orders = []

            for order_id in flight_order_ids:
                response = requests.get(
                    f"{self.base_url}/air/orders/{order_id}",
                    headers=self.headers,
                )
                response.raise_for_status()

                flight_orders.append(response.json())

            return flight_orders

        except requests.exceptions.RequestException as error:
            raise error


duffel_flight_service = DuffelFlightService()
