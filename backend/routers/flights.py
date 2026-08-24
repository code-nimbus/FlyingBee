import uuid as uuid_module
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.application.bookings.cancel_booking import (
    BookingAlreadyCancelled,
    BookingCannotBeCancelled,
    BookingNotFound,
    CancelBooking,
    CancelBookingCommand,
)
from backend.application.bookings.create_flight_order import (
    CreateFlightOrder,
    FlightOrderProviderError,
    InvalidFlightOrderRequest,
)
from backend.application.bookings.get_booking_details import (
    BookingDetailsNotFound,
    GetBookingDetails,
)
from backend.application.bookings.get_seat_map import (
    GetSeatMap,
    InvalidSeatMapRequest,
    SeatMapBookingNotFound,
    SeatMapProviderError,
)
from backend.application.bookings.get_user_bookings import GetUserBookings
from backend.application.flights.confirm_flight_price import (
    ConfirmFlightPrice,
    FlightPricingProviderError,
    InvalidFlightPricingRequest,
)
from backend.application.flights.get_seat_map_from_flight_offer import (
    GetSeatMapFromFlightOffer,
    InvalidSeatMapOfferRequest,
    SeatMapFromOfferProviderError,
)
from backend.application.flights.search_flights import (
    FlightSearchProviderError,
    InvalidFlightSearchRequest,
    SearchFlights,
)
from backend.application.flights.search_locations import (
    InvalidLocationSearchRequest,
    LocationSearchProviderError,
    SearchLocations,
)
from backend.crud.database import get_session
from backend.external_services.cache import redis_cache
from backend.external_services.duffel import duffel_flight_service
from backend.infrastructure.bookings.booking_success_presenter import (
    BookingSuccessPresenter,
)
from backend.infrastructure.bookings.kafka_booking_event_publisher import (
    KafkaBookingEventPublisher,
)
from backend.infrastructure.bookings.redis_user_booking_cache import (
    RedisUserBookingCache,
)
from backend.infrastructure.bookings.sqlmodel_booking_repository import (
    SqlModelBookingRepository,
)
from backend.infrastructure.flights.duffel_flight_order_cancellation_gateway import (
    DuffelFlightOrderCancellationGateway,
)
from backend.infrastructure.flights.duffel_flight_order_gateway import (
    DuffelFlightOrderGateway,
)
from backend.infrastructure.flights.duffel_location_search_gateway import (
    DuffelLocationSearchGateway,
)
from backend.infrastructure.flights.duffel_pricing_gateway import (
    DuffelPricingGateway,
)
from backend.infrastructure.flights.duffel_search_gateway import (
    DuffelSearchGateway,
)
from backend.infrastructure.flights.duffel_seat_map_gateway import (
    DuffelSeatMapGateway,
)
from backend.infrastructure.redis import async_redis
from backend.models.users import UserInDB
from backend.schemas.bookings import (
    BookingCancellationResponse,
    BookingResponse,
    CursorPaginatedUserBookingResponse,
    UserBookingResponse,
)
from backend.schemas.flight_order import FlightOrderRequestBody
from backend.schemas.flight_price_confirm import FlightOffer
from backend.schemas.flight_search import FlightSearchRequestGet
from backend.schemas.flights import FlightPricingResponse
from backend.schemas.locations import (
    AirportCitySearchRequest as LocationSearchRequest,
)
from backend.schemas.locations import (
    AirportCitySearchResponse as LocationSearchResponse,
)

# from backend.utils.kafka import kafka_producer
from backend.utils.kafka import KafkaProducerService
from backend.utils.log_manager import get_app_logger
from backend.utils.pagination import MAX_PAGINATION_LIMIT
from backend.utils.security import get_current_user

logger = get_app_logger(__name__)

router = APIRouter()


def get_kafka_producer() -> KafkaProducerService:
    return KafkaProducerService()


def get_search_flights_use_case() -> SearchFlights:
    return SearchFlights(
        provider=DuffelSearchGateway(duffel_flight_service),
        cache=redis_cache,
    )


def get_confirm_flight_price_use_case() -> ConfirmFlightPrice:
    return ConfirmFlightPrice(
        provider=DuffelPricingGateway(duffel_flight_service),
    )


def get_create_flight_order_use_case(
    session: Session = Depends(get_session),
) -> CreateFlightOrder:
    kafka_producer = KafkaProducerService()

    return CreateFlightOrder(
        order_provider=DuffelFlightOrderGateway(duffel_flight_service),
        booking_repository=SqlModelBookingRepository(session),
        booking_cache=RedisUserBookingCache(async_redis),
        event_publisher=KafkaBookingEventPublisher(kafka_producer),
    )


def get_booking_details_use_case(
    session: Session = Depends(get_session),
) -> GetBookingDetails:
    return GetBookingDetails(
        booking_repository=SqlModelBookingRepository(session),
        presenter=BookingSuccessPresenter(),
    )


def get_cancel_booking_use_case(
    session: Session = Depends(get_session),
) -> CancelBooking:
    kafka_producer = KafkaProducerService()
    return CancelBooking(
        booking_repository=SqlModelBookingRepository(session),
        booking_cancellation_provider=DuffelFlightOrderCancellationGateway(
            duffel_flight_service
        ),
        booking_cache=RedisUserBookingCache(async_redis),
        event_publisher=KafkaBookingEventPublisher(kafka_producer),
    )


def get_seat_map_use_case(
    session: Session = Depends(get_session),
) -> GetSeatMap:
    return GetSeatMap(
        booking_repository=SqlModelBookingRepository(session),
        seat_map_provider=DuffelSeatMapGateway(duffel_flight_service),
    )


def get_seat_map_from_flight_offer_use_case() -> GetSeatMapFromFlightOffer:
    return GetSeatMapFromFlightOffer(
        seat_map_provider=DuffelSeatMapGateway(duffel_flight_service),
    )


def get_location_search_use_case() -> SearchLocations:
    return SearchLocations(
        provider=DuffelLocationSearchGateway(duffel_flight_service),
        cache=redis_cache,
    )


def get_user_bookings_use_case(
    session: Session = Depends(get_session),
) -> GetUserBookings:
    return GetUserBookings(
        booking_repository=SqlModelBookingRepository(session),
        cache=RedisUserBookingCache(async_redis),
    )


@router.get("/shopping/flight-offers")
async def search_flights_get(
    request: Annotated[FlightSearchRequestGet, Query()],
    search_flights_use_case: SearchFlights = Depends(get_search_flights_use_case),
):
    try:
        return search_flights_use_case.execute(request.model_dump(exclude_none=True))

    except InvalidFlightSearchRequest:
        raise HTTPException(
            status_code=400,
            detail="Invalid request parameters",
        )

    except FlightSearchProviderError:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for flights",
        )

    except Exception:
        logger.exception("Unexpected error while searching for flights")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for flights",
        )


@router.post(
    "/shopping/flight-offers/pricing",
    response_model=FlightPricingResponse,
)
async def confirm_price(
    request: FlightOffer,
    confirm_flight_price_use_case: ConfirmFlightPrice = Depends(
        get_confirm_flight_price_use_case
    ),
):
    try:
        return confirm_flight_price_use_case.execute(request.model_dump())

    except InvalidFlightPricingRequest:
        raise HTTPException(
            status_code=400,
            detail="Invalid pricing request",
        )

    except FlightPricingProviderError:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while confirming flight pricing",
        )

    except Exception:
        logger.exception("Unexpected error while confirming flight pricing")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while confirming flight pricing",
        )


@router.post(
    "/booking/flight-orders",
    response_model=BookingResponse,
)
async def flight_order(
    request: FlightOrderRequestBody,
    current_user: UserInDB = Depends(get_current_user),
    create_flight_order_use_case: CreateFlightOrder = Depends(
        get_create_flight_order_use_case
    ),
):
    logger.info(f"Flight order creation initiated by user_id: {current_user.id}")

    try:
        # booking = create_flight_order_use_case.execute(
        #     user_id=current_user.id,
        #     user_email=current_user.email,
        #     order_request=request.model_dump(by_alias=True),
        # )
        booking = await create_flight_order_use_case.execute(
            user_id=current_user.id,
            user_email=current_user.email,
            # order_request=request.model_dump(
            #     mode="json",
            #     by_alias=True,
            # ),
            order_request=request.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
            ),
        )

        response = BookingResponse(
            id=booking.id,
            flight_order_id=booking.flight_order_id,
            status=booking.status,
        )

        logger.info(
            f"Booking record saved successfully for user_id: "
            f"{current_user.id}, "
            f"flight_order_id: {booking.flight_order_id}"
        )

        return response

    except InvalidFlightOrderRequest as e:
        logger.warning(
            f"Invalid flight order request for user_id: {current_user.id}: {e!s}"
        )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except FlightOrderProviderError:
        logger.exception(
            f"Duffel provider error during order creation "
            f"for user_id: {current_user.id}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred while creating "
                "the flight order. Please try again."
            ),
        )

    except Exception:
        logger.exception(
            f"Unexpected error during flight order creation "
            f"for user_id: {current_user.id}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred while creating "
                "the flight order. Please try again."
            ),
        )


@router.get("/shopping/seatmaps")
async def view_seat_map_get(
    flight_order_id: Annotated[str, Query(alias="flightorderId")],
    current_user: UserInDB = Depends(get_current_user),
    seat_map_use_case: GetSeatMap = Depends(get_seat_map_use_case),
):
    try:
        logger.info(
            "Seat map request started | flight_order_reference=%s | user_id=%s",
            flight_order_id,
            current_user.id,
        )
        result = seat_map_use_case.execute(
            flight_order_id=flight_order_id,
            user_id=current_user.id,
        )

        logger.info(
            "Seat map request succeeded | flight_order_reference=%s",
            flight_order_id,
        )

        return result

    except SeatMapBookingNotFound:
        logger.warning(
            "Seat map booking not found | flight_order_reference=%s | user_id=%s",
            flight_order_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=404,
            detail="Booking not found or access denied",
        )

    except InvalidSeatMapRequest as e:
        logger.warning("Invalid seat map request: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except SeatMapProviderError:
        logger.exception(
            "Seat map provider error | flight_order_reference=%s",
            flight_order_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve seat map",
        )

    # except HTTPException:
    #     raise

    except Exception:
        # logger.exception(
        #     f"Failed to retrieve seat map for ID: "
        #     f"{flight_order_reference}"
        # )
        logger.exception(
            "UNEXPECTED SEAT MAP ERROR | flight_order_reference=%s | user_id=%s",
            flight_order_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve seat map",
        )


@router.post("/shopping/seatmaps")
async def view_seat_map_post(
    request: FlightOffer,
    seat_map_from_offer_use_case: GetSeatMapFromFlightOffer = Depends(
        get_seat_map_from_flight_offer_use_case
    ),
):
    try:
        return seat_map_from_offer_use_case.execute(request.model_dump())

    except InvalidSeatMapOfferRequest as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except SeatMapFromOfferProviderError:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve seat map",
        )

    except Exception:
        logger.exception("Failed to retrieve seat map from flight offer")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve seat map from flight offer",
        )


@router.get("/booking/flight-orders/{booking_id}")
async def get_booking_details(
    booking_id: str,
    current_user: UserInDB = Depends(get_current_user),
    booking_details_use_case: GetBookingDetails = Depends(get_booking_details_use_case),
):
    logger.info(
        f"Fetching booking details for booking_id: "
        f"{booking_id}, user_id: {current_user.id}"
    )

    try:
        try:
            booking_uuid = uuid_module.UUID(booking_id)

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid booking ID format",
            )

        booking_details = booking_details_use_case.execute(
            booking_id=booking_uuid,
            user_id=current_user.id,
            user_email=current_user.email,
        )

        logger.info(
            f"Successfully retrieved booking details for booking_id: {booking_id}"
        )

        return booking_details

    except HTTPException:
        raise

    except BookingDetailsNotFound:
        raise HTTPException(
            status_code=404,
            detail=("Booking not found or you don't have permission to access it"),
        )

    except Exception:
        logger.exception(f"Error fetching booking details for booking_id: {booking_id}")

        raise HTTPException(
            status_code=500,
            detail=("An error occurred while retrieving the booking details"),
        )


@router.delete("/booking/flight-orders/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: UserInDB = Depends(get_current_user),
    cancel_booking_use_case: CancelBooking = Depends(get_cancel_booking_use_case),
):
    logger.info(
        f"Booking cancellation initiated for booking_id: "
        f"{booking_id}, user_id: {current_user.id}"
    )

    try:
        try:
            booking_uuid = uuid_module.UUID(booking_id)

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid booking ID format",
            )

        cancelled_booking = cancel_booking_use_case.execute(
            command=CancelBookingCommand(
                booking_id=booking_uuid,
                user_id=current_user.id,
                user_email=current_user.email,
            )
        )

        return BookingCancellationResponse(
            id=cancelled_booking.id,
            status=cancelled_booking.status,
            message=cancelled_booking.message,
        )

    except BookingNotFound:
        raise HTTPException(
            status_code=404,
            detail=("Booking not found or you don't have permission to cancel it"),
        )

    except BookingAlreadyCancelled:
        raise HTTPException(
            status_code=400,
            detail="This booking has already been cancelled",
        )

    except BookingCannotBeCancelled:
        raise HTTPException(
            status_code=400,
            detail=(
                "Booking with status 'reversed', 'failed', "
                "or 'refunded' cannot be cancelled"
            ),
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            f"Error cancelling booking for booking_id: "
            f"{booking_id}, user_id: {current_user.id}"
        )

        raise HTTPException(
            status_code=500,
            detail="An error occurred while cancelling the booking",
        )


@router.get(
    "/reference-data/locations",
    response_model=list[LocationSearchResponse],
)
async def search_locations(
    request: Annotated[LocationSearchRequest, Query()],
    location_search_use_case: SearchLocations = Depends(get_location_search_use_case),
):
    try:
        return location_search_use_case.execute(request.model_dump())

    except InvalidLocationSearchRequest:
        raise HTTPException(
            status_code=400,
            detail="Invalid location search request",
        )

    except LocationSearchProviderError:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for a location",
        )

    except Exception:
        logger.exception("Unexpected error while searching for a location")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for a location",
        )


@router.get(
    "/bookings",
    response_model=CursorPaginatedUserBookingResponse,
)
async def get_user_bookings(
    cursor: str | None = Query(
        None,
        description="Cursor for pagination",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=MAX_PAGINATION_LIMIT,
        description="Maximum number of records to return",
    ),
    include_count: bool = Query(
        False,
        description="Include total_count in response (may be slower)",
    ),
    user: UserInDB = Depends(get_current_user),
    user_bookings_use_case: GetUserBookings = Depends(get_user_bookings_use_case),
):
    try:
        user_bookings_page = await user_bookings_use_case.execute(
            user_id=user.id,
            cursor=cursor,
            limit=limit,
            include_count=include_count,
        )

        response = CursorPaginatedUserBookingResponse(
            items=[
                UserBookingResponse(
                    id=booking.id,
                    pnr=booking.pnr,
                    status=booking.status,
                    created_at=booking.created_at,
                    ticket_url=booking.ticket_url,
                )
                for booking in user_bookings_page.items
            ],
            next_cursor=user_bookings_page.next_cursor,
            has_more=user_bookings_page.has_more,
            has_previous=user_bookings_page.has_previous,
            total_count=user_bookings_page.total_count,
            limit=user_bookings_page.limit,
        )

        logger.info(
            f"Successfully fetched {len(response.items)} bookings "
            f"for user_id: {user.id} "
            f"(has_more: {response.has_more})"
        )

        return response

    except Exception:
        logger.exception(f"Error fetching bookings for user_id: {user.id}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching bookings",
        )
