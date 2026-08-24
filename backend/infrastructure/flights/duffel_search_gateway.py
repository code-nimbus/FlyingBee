import logging
from typing import Any

from backend.application.flights.search_flights import (
    FlightSearchProviderError,
    FlightSearchResult,
    InvalidFlightSearchRequest,
)
from backend.external_services.interface import FlightServiceProtocol

logger = logging.getLogger(__name__)


class DuffelSearchGateway:
    def __init__(
        self,
        flight_service: FlightServiceProtocol,
    ):
        self.flight_service = flight_service

    def search(
        self,
        criteria: dict[str, Any],
    ) -> FlightSearchResult:
        try:
            request_body = self._build_duffel_request(criteria)

            # response = self.flight_service.search_flights(
            #     request_body
            # )
            logger.info(
                "Duffel search request: %s",
                request_body,
            )

            response = self.flight_service.search_flights(request_body)

            logger.info("Duffel request: %s", request_body)
            logger.info("Duffel response: %s", response)

            return self._transform_response(
                response,
                criteria,
            )

        except InvalidFlightSearchRequest:
            raise

        except ValueError as exc:
            raise InvalidFlightSearchRequest(str(exc)) from exc

        # except Exception as exc:
        #     raise FlightSearchProviderError(
        #         "Duffel flight search failed"
        #     ) from exc

        except Exception as exc:
            logger.exception("Duffel flight search failed")

            raise FlightSearchProviderError("Duffel flight search failed") from exc

    @staticmethod
    def _build_duffel_request(
        criteria: dict[str, Any],
    ) -> dict[str, Any]:
        origin = criteria.get("originLocationCode")
        destination = criteria.get("destinationLocationCode")
        departure_date = criteria.get("departureDate")

        if not origin:
            raise InvalidFlightSearchRequest("originLocationCode is required")

        if not destination:
            raise InvalidFlightSearchRequest("destinationLocationCode is required")

        if not departure_date:
            raise InvalidFlightSearchRequest("departureDate is required")

        passengers = []

        adults = criteria.get("adults", 1)
        children = criteria.get("children", 0) or 0
        infants = criteria.get("infants", 0) or 0

        for _ in range(adults):
            passengers.append(
                {
                    "type": "adult",
                }
            )

        for _ in range(children):
            passengers.append(
                {
                    "type": "child",
                }
            )

        for _ in range(infants):
            passengers.append(
                {
                    "type": "infant_without_seat",
                }
            )

        slices = [
            {
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": departure_date,
            }
        ]

        return_date = criteria.get("returnDate")

        if return_date:
            slices.append(
                {
                    "origin": destination.upper(),
                    "destination": origin.upper(),
                    "departure_date": return_date,
                }
            )

        request_body: dict[str, Any] = {
            "data": {
                "slices": slices,
                "passengers": passengers,
            }
        }

        travel_class = criteria.get("travelClass")

        if travel_class:
            cabin_class = travel_class.lower()

            cabin_mapping = {
                "economy": "economy",
                "premium_economy": "premium_economy",
                "premium-economy": "premium_economy",
                "business": "business",
                "first": "first",
            }

            if cabin_class in cabin_mapping:
                request_body["data"]["cabin_class"] = cabin_mapping[cabin_class]

        return request_body

    # @staticmethod
    # def _transform_response(
    #     response: dict[str, Any],
    #     criteria: dict[str, Any],
    # ) -> FlightSearchResult:
    #     data = response.get("data", [])

    #     if not isinstance(data, list):
    #         raise FlightSearchProviderError(
    #             "Invalid response received from Duffel"
    #         )

    #     results: FlightSearchResult = []

    #     max_results = criteria.get("max", 5)

    #     for offer in data[:max_results]:
    #         if not isinstance(offer, dict):
    #             continue

    #         slices = offer.get("slices", [])

    #         first_slice = (
    #             slices[0]
    #             if slices and isinstance(slices[0], dict)
    #             else {}
    #         )

    #         segments = first_slice.get("segments", [])

    #         first_segment = (
    #             segments[0]
    #             if segments
    #             and isinstance(segments[0], dict)
    #             else {}
    #         )

    #         last_segment = (
    #             segments[-1]
    #             if segments
    #             and isinstance(segments[-1], dict)
    #             else {}
    #         )

    #         origin = first_segment.get(
    #             "origin",
    #             {},
    #         )

    #         destination = last_segment.get(
    #             "destination",
    #             {},
    #         )

    #         results.append(
    #             {
    #                 "id": offer.get("id"),
    #                 "price": {
    #                     "amount": offer.get("total_amount"),
    #                     "currency": offer.get("total_currency"),
    #                 },
    #                 "origin": {
    #                     "iata_code": origin.get("iata_code"),
    #                     "name": origin.get("name"),
    #                     "city_name": origin.get("city_name"),
    #                 },
    #                 "destination": {
    #                     "iata_code": destination.get("iata_code"),
    #                     "name": destination.get("name"),
    #                     "city_name": destination.get("city_name"),
    #                 },
    #                 "departure_date": criteria.get(
    #                     "departureDate"
    #                 ),
    #                 "return_date": criteria.get(
    #                     "returnDate"
    #                 ),
    #                 "slices": slices,
    #                 "raw_offer": offer,
    #             }
    #         )

    #     return results

    @staticmethod
    def _transform_response(
        response: dict[str, Any],
        criteria: dict[str, Any],
    ) -> FlightSearchResult:
        if not isinstance(response, dict):
            raise FlightSearchProviderError("Invalid response received from Duffel")

        data = response.get("data")

        if not isinstance(data, dict):
            raise FlightSearchProviderError(
                "Invalid Duffel response: data must be an object"
            )

        offers = data.get("offers", [])

        if not isinstance(offers, list):
            raise FlightSearchProviderError(
                "Invalid Duffel response: offers must be a list"
            )

        results: FlightSearchResult = []

        max_results = criteria.get("max", 5)
        max_price = criteria.get("maxPrice")
        currency_code = criteria.get("currencyCode")

        for offer in offers:
            if not isinstance(offer, dict):
                continue

            # ----------------------------------------
            # PRICE FILTER
            # ----------------------------------------
            total_amount = offer.get("total_amount")
            total_currency = offer.get("total_currency")

            if max_price is not None:
                try:
                    if float(total_amount) > float(max_price):
                        continue
                except (TypeError, ValueError):
                    continue

            # ----------------------------------------
            # CURRENCY FILTER
            # ----------------------------------------
            if currency_code:
                if total_currency != currency_code:
                    continue

            # ----------------------------------------
            # LIMIT RESULTS
            # ----------------------------------------
            if len(results) >= max_results:
                break

            slices = offer.get("slices", [])

            if not isinstance(slices, list):
                continue

            if not slices:
                continue

            first_slice = slices[0] if isinstance(slices[0], dict) else {}

            segments = first_slice.get("segments", [])

            if not isinstance(segments, list):
                continue

            if not segments:
                continue

            first_segment = segments[0] if isinstance(segments[0], dict) else {}

            last_segment = segments[-1] if isinstance(segments[-1], dict) else {}

            origin = first_segment.get("origin", {})
            destination = last_segment.get("destination", {})

            if not isinstance(origin, dict):
                origin = {}

            if not isinstance(destination, dict):
                destination = {}

            results.append(
                {
                    "id": offer.get("id"),
                    "price": {
                        "amount": total_amount,
                        "currency": total_currency,
                    },
                    "origin": {
                        "iata_code": origin.get("iata_code"),
                        "name": origin.get("name"),
                        "city_name": origin.get("city_name"),
                    },
                    "destination": {
                        "iata_code": destination.get("iata_code"),
                        "name": destination.get("name"),
                        "city_name": destination.get("city_name"),
                    },
                    "departure_date": criteria.get("departureDate"),
                    "return_date": criteria.get("returnDate"),
                    "slices": slices,
                    "raw_offer": offer,
                }
            )

        return results
