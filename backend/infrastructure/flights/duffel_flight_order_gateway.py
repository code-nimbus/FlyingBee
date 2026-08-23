from typing import Any

from backend.external_services.duffel import DuffelFlightService


class DuffelFlightOrderGateway:
    def __init__(
        self,
        duffel_service: DuffelFlightService,
    ):
        self.duffel_service = duffel_service

    def create_flight_order(
        self,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        return self.duffel_service.create_flight_order(request_body)
