from typing import Any

from pydantic import BaseModel, ConfigDict


class Airport(BaseModel):
    iata_code: str
    name: str
    city_name: str


class Location(BaseModel):
    iata_code: str
    name: str
    city_name: str


class Aircraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    iata_code: str | None = None
    name: str | None = None


class Airline(BaseModel):
    model_config = ConfigDict(extra="allow")

    iata_code: str | None = None
    name: str | None = None


class FlightSegment(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    origin: Location
    destination: Location
    departure_time: str
    arrival_time: str

    marketing_carrier: Airline | None = None
    operating_carrier: Airline | None = None

    marketing_carrier_flight_number: str | None = None
    operating_carrier_flight_number: str | None = None

    aircraft: Aircraft | None = None

    duration: int | None = None
    distance: int | None = None

    stops: list[dict[str, Any]] | None = None

    passengers: list[dict[str, Any]] | None = None


class Slice(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    origin: Location
    destination: Location

    duration: int | None = None
    segments: list[FlightSegment]


class MoneyAmount(BaseModel):
    amount: str
    currency: str


class BaggageAllowance(BaseModel):
    model_config = ConfigDict(extra="allow")

    quantity: int | None = None
    weight: int | None = None
    weight_unit: str | None = None


class PassengerService(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    type: str | None = None
    quantity: int | None = None
    total_amount: str | None = None
    total_currency: str | None = None


class Passenger(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    type: str | None = None

    age: int | None = None

    given_name: str | None = None
    family_name: str | None = None

    fare_basis_code: str | None = None

    baggage_allowance: BaggageAllowance | None = None

    services: list[PassengerService] | None = None


class FlightOffer(BaseModel):
    """
    Duffel flight offer used when requesting a seat map
    for a specific flight offer.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    type: str

    total_amount: str
    total_currency: str

    base_amount: str | None = None
    base_currency: str | None = None

    tax_amount: str | None = None
    tax_currency: str | None = None

    slices: list[Slice]

    passengers: list[Passenger] | None = None

    expires_at: str | None = None

    owner: Airline | None = None

    conditions: dict[str, Any] | None = None

    payment_requirements: dict[str, Any] | None = None

    supported_passenger_identity_document_types: list[str] | None = None

    private_fares: list[dict[str, Any]] | None = None

    metadata: dict[str, Any] | None = None

    available_services: list[dict[str, Any]] | None = None
