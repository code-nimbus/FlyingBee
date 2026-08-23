from pydantic import BaseModel, Field, field_validator


class DepartureDateTimeRange(BaseModel):
    date: str
    time: str


class OriginDestination(BaseModel):
    id: str
    originLocationCode: str
    destinationLocationCode: str
    departureDateTimeRange: DepartureDateTimeRange


class Traveler(BaseModel):
    id: str
    travelerType: str
    associatedAdultId: str | None = None


class AdditionalInformation(BaseModel):
    chargeableCheckedBags: bool
    brandedFares: bool
    fareRules: bool


class PricingOptions(BaseModel):
    includedCheckedBagsOnly: bool


class CarrierRestrictions(BaseModel):
    blacklistedInEUAllowed: bool
    includedCarrierCodes: list[str]


class CabinRestriction(BaseModel):
    cabin: str
    coverage: str
    originDestinationIds: list[str]


class ConnectionRestriction(BaseModel):
    airportChangeAllowed: bool
    technicalStopsAllowed: bool


class FlightFilters(BaseModel):
    crossBorderAllowed: bool
    moreOvernightsAllowed: bool
    returnToDepartureAirport: bool
    railSegmentAllowed: bool
    busSegmentAllowed: bool
    carrierRestrictions: CarrierRestrictions
    cabinRestrictions: list[CabinRestriction]
    connectionRestriction: ConnectionRestriction


class SearchCriteria(BaseModel):
    excludeAllotments: bool
    addOneWayOffers: bool
    maxFlightOffers: int
    allowAlternativeFareOptions: bool
    oneFlightOfferPerDay: bool
    additionalInformation: AdditionalInformation
    pricingOptions: PricingOptions
    flightFilters: FlightFilters


class FlightSearchRequestPost(BaseModel):
    currencyCode: str
    originDestinations: list[OriginDestination]
    travelers: list[Traveler]
    sources: list[str]
    searchCriteria: SearchCriteria


class FlightSearchRequestGet(BaseModel):
    originLocationCode: str
    destinationLocationCode: str
    departureDate: str

    adults: int = Field(
        default=1,
        ge=1,
    )

    max: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    returnDate: str | None = None

    children: int | None = Field(
        default=None,
        ge=0,
    )

    infants: int | None = Field(
        default=None,
        ge=0,
    )

    travelClass: str | None = None

    includedAirlineCodes: str | None = None

    excludedAirlineCodes: str | None = None

    nonStop: bool | None = None

    currencyCode: str = Field(
        default="USD",
    )

    maxPrice: int | None = Field(
        default=None,
        ge=0,
    )

    @field_validator(
        "originLocationCode",
        "destinationLocationCode",
        mode="before",
    )
    @classmethod
    def uppercase_airport_code(
        cls,
        value: str,
    ) -> str:
        if not isinstance(value, str):
            return value

        return value.strip().upper()

    @field_validator("travelClass", mode="before")
    @classmethod
    def normalize_travel_class(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip().lower()

    @field_validator("currencyCode", mode="before")
    @classmethod
    def uppercase_currency(
        cls,
        value: str,
    ) -> str:
        if not isinstance(value, str):
            return value

        return value.strip().upper()
