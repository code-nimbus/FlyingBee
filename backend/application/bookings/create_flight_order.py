from typing import Any
from uuid import UUID

from backend.models.booking import Booking


class InvalidFlightOrderRequest(Exception):
    pass


class FlightOrderProviderError(Exception):
    pass


class CreateFlightOrder:
    def __init__(
        self,
        order_provider,
        booking_repository,
        booking_cache,
        event_publisher,
    ):
        self.order_provider = order_provider
        self.booking_repository = booking_repository
        self.booking_cache = booking_cache
        self.event_publisher = event_publisher

    async def execute(
        self,
        user_id: UUID,
        user_email: str,
        order_request: dict[str, Any],
    ):
        if not isinstance(order_request, dict):
            raise InvalidFlightOrderRequest("Invalid order request")

        offer_id = order_request.get("offer_id")
        passengers = order_request.get("passengers")

        if not offer_id:
            raise InvalidFlightOrderRequest("offer_id is required")

        if not passengers:
            raise InvalidFlightOrderRequest("At least one passenger is required")

        try:
            # ---------------------------------------------------------
            # 1. Build Duffel request
            # ---------------------------------------------------------
            duffel_request = self._build_duffel_request(order_request)

            print("DUFFEL REQUEST:", duffel_request)

            # ---------------------------------------------------------
            # 2. Create order with Duffel
            # ---------------------------------------------------------
            response = self.order_provider.create_flight_order(duffel_request)

            if not isinstance(response, dict):
                raise FlightOrderProviderError("Invalid response from flight provider")

            duffel_data = response.get("data")

            if not isinstance(duffel_data, dict):
                raise FlightOrderProviderError("Invalid flight order response")

            flight_order_id = duffel_data.get("id")

            if not flight_order_id:
                raise FlightOrderProviderError(
                    "Flight order ID missing from provider response"
                )

            # ---------------------------------------------------------
            # 3. Create Booking SQLModel
            # ---------------------------------------------------------
            booking = Booking(
                user_id=user_id,
                user_email=user_email,
                flight_order_id=flight_order_id,
                status=duffel_data.get("status", "pending"),
                order_data=duffel_data,
            )

            # ---------------------------------------------------------
            # 4. Save booking
            # ---------------------------------------------------------
            booking = self.booking_repository.create(booking)

            # ---------------------------------------------------------
            # 5. Invalidate Redis cache
            # ---------------------------------------------------------
            await self.booking_cache.invalidate_user_bookings(user_id)

            # ---------------------------------------------------------
            # 6. Publish Kafka event
            # ---------------------------------------------------------
            self.event_publisher.publish_booking_created(booking)

            # ---------------------------------------------------------
            # 7. Return persisted booking
            # ---------------------------------------------------------
            return booking

        except InvalidFlightOrderRequest:
            raise

        except FlightOrderProviderError:
            raise

        except Exception as error:
            raise FlightOrderProviderError("Failed to create flight order") from error

    @staticmethod
    def _build_duffel_request(
        order_request: dict[str, Any],
    ) -> dict[str, Any]:
        offer_id = order_request["offer_id"]
        passengers = order_request["passengers"]
        order_type = order_request.get("type", "hold")

        if not isinstance(passengers, list) or not passengers:
            raise InvalidFlightOrderRequest("At least one passenger is required")

        sanitized_passengers = []

        for passenger in passengers:
            if not isinstance(passenger, dict):
                raise InvalidFlightOrderRequest("Each passenger must be an object")

            # passenger_data = passenger.copy()

            # # Never send a client-generated passenger ID to Duffel.
            # passenger_data.pop("id", None)

            # sanitized_passengers.append(
            #     passenger_data
            # )

            passenger_data = {
                key: value for key, value in passenger.items() if value is not None
            }

            sanitized_passengers.append(passenger_data)

        data: dict[str, Any] = {
            "type": order_type,
            "selected_offers": [offer_id],
            "passengers": sanitized_passengers,
        }

        if order_request.get("users"):
            data["users"] = order_request["users"]

        if order_request.get("services"):
            data["services"] = order_request["services"]

        if order_request.get("metadata"):
            data["metadata"] = order_request["metadata"]

        if order_type == "instant":
            payments = order_request.get("payments")

            if not payments:
                raise InvalidFlightOrderRequest(
                    "payments are required for instant orders"
                )

            data["payments"] = payments

        return {"data": data}


# from typing import Any
# from uuid import UUID

# from models.booking import Booking


# class InvalidFlightOrderRequest(Exception):
#     pass


# class FlightOrderProviderError(Exception):
#     pass


# class CreateFlightOrder:
#     def __init__(
#         self,
#         order_provider,
#         booking_repository,
#         booking_cache,
#         event_publisher,
#     ):
#         self.order_provider = order_provider
#         self.booking_repository = booking_repository
#         self.booking_cache = booking_cache
#         self.event_publisher = event_publisher

#     def execute(
#         self,
#         user_id: UUID,
#         user_email: str,
#         order_request: dict[str, Any],
#     ):
#         if not isinstance(order_request, dict):
#             raise InvalidFlightOrderRequest(
#                 "Invalid order request"
#             )

#         offer_id = order_request.get("offer_id")
#         passengers = order_request.get("passengers")

#         if not offer_id:
#             raise InvalidFlightOrderRequest(
#                 "offer_id is required"
#             )

#         if not passengers:
#             raise InvalidFlightOrderRequest(
#                 "At least one passenger is required"
#             )

#         try:
#             # ---------------------------------------------------------
#             # 1. Build Duffel request
#             # ---------------------------------------------------------
#             duffel_request = self._build_duffel_request(
#                 order_request
#             )

#             # ---------------------------------------------------------
#             # 2. Create order with Duffel
#             # ---------------------------------------------------------
#             response = self.order_provider.create_flight_order(
#                 duffel_request
#             )

#             if not isinstance(response, dict):
#                 raise FlightOrderProviderError(
#                     "Invalid response from flight provider"
#                 )

#             duffel_data = response.get("data")

#             if not isinstance(duffel_data, dict):
#                 raise FlightOrderProviderError(
#                     "Invalid flight order response"
#                 )

#             flight_order_id = duffel_data.get("id")

#             if not flight_order_id:
#                 raise FlightOrderProviderError(
#                     "Flight order ID missing from provider response"
#                 )

#             # ---------------------------------------------------------
#             # 3. Create Booking SQLModel
#             # ---------------------------------------------------------
#             booking = Booking(
#                 user_id=user_id,
#                 user_email=user_email,
#                 flight_order_id=flight_order_id,
#                 status=duffel_data.get("status", "pending"),
#                 order_data=duffel_data,
#             )

#             # ---------------------------------------------------------
#             # 4. Save booking
#             # ---------------------------------------------------------
#             booking = self.booking_repository.create(
#                 booking
#             )

#             # ---------------------------------------------------------
#             # 5. Invalidate Redis cache
#             # ---------------------------------------------------------
#             self.booking_cache.invalidate_user_bookings(
#                 user_id
#             )

#             # ---------------------------------------------------------
#             # 6. Publish Kafka event
#             # ---------------------------------------------------------
#             self.event_publisher.publish(
#                 booking
#             )

#             # ---------------------------------------------------------
#             # 7. Return persisted booking
#             # ---------------------------------------------------------
#             return booking

#         except InvalidFlightOrderRequest:
#             raise

#         except FlightOrderProviderError:
#             raise

#         except Exception as error:
#             raise FlightOrderProviderError(
#                 "Failed to create flight order"
#             ) from error

#     # @staticmethod
#     # def _build_duffel_request(
#     #     order_request: dict[str, Any],
#     # ) -> dict[str, Any]:

#     #     offer_id = order_request["offer_id"]
#     #     passengers = order_request["passengers"]
#     #     order_type = order_request.get("type", "hold")

#     #     data: dict[str, Any] = {
#     #         "type": order_type,
#     #         "selected_offers": [offer_id],
#     #         "passengers": passengers,
#     #     }

#     #     if order_request.get("users"):
#     #         data["users"] = order_request["users"]

#     #     if order_request.get("services"):
#     #         data["services"] = order_request["services"]

#     #     if order_request.get("metadata"):
#     #         data["metadata"] = order_request["metadata"]

#     #     if order_type == "instant":
#     #         payments = order_request.get("payments")

#     #         if not payments:
#     #             raise InvalidFlightOrderRequest(
#     #                 "payments are required for instant orders"
#     #             )

#     #         data["payments"] = payments

#     #     return {
#     #         "data": data
#     #     }

#     @staticmethod
#     def _build_duffel_request(
#         order_request: dict[str, Any],
#     ) -> dict[str, Any]:

#         offer_id = order_request["offer_id"]
#         passengers = order_request["passengers"]
#         order_type = order_request.get("type", "hold")

#         if not isinstance(passengers, list) or not passengers:
#             raise InvalidFlightOrderRequest(
#                 "At least one passenger is required"
#             )

#         sanitized_passengers = []

#         for passenger in passengers:
#             if not isinstance(passenger, dict):
#                 raise InvalidFlightOrderRequest(
#                     "Each passenger must be an object"
#                 )

#             passenger_data = passenger.copy()

#             # Do NOT send a client-generated Duffel passenger ID.
#             passenger_data.pop("id", None)

#             sanitized_passengers.append(passenger_data)

#         data: dict[str, Any] = {
#             "type": order_type,
#             "selected_offers": [offer_id],
#             "passengers": sanitized_passengers,
#         }

#         if order_request.get("users"):
#             data["users"] = order_request["users"]

#         if order_request.get("services"):
#             data["services"] = order_request["services"]

#         if order_request.get("metadata"):
#             data["metadata"] = order_request["metadata"]

#         if order_type == "instant":
#             payments = order_request.get("payments")

#             if not payments:
#                 raise InvalidFlightOrderRequest(
#                     "payments are required for instant orders"
#                 )

#             data["payments"] = payments

#         return {
#             "data": data
#         }
