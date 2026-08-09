from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Annotated

from backend.crud.database import get_session
from backend.crud.orders import create_order

from backend.external_services.travelpayouts import search_flights
from backend.external_services.cache import redis_cache

from backend.models.orders import FlightOrder, Traveler
from backend.models.bookings import Booking
from backend.models.users import UserInDB

from backend.schemas.flights import FlightSearch
from backend.schemas.orders import (
    FlightOrderRequest,
)
from backend.schemas.flights import FlightOffer
from backend.schemas.bookings import BookingResponse

from backend.dependencies import get_current_user

import logging
import json

logger = logging.getLogger(__name__)


# Keep the router structure simple.
# The routes below intentionally match the Nehemiah tutorial.
router = APIRouter(prefix="/api")


# ============================================================
# Dependency Layer
# ============================================================


def get_search_flights_use_case():
    """
    Tutorial-compatible dependency name.

    In the original Nehemiah implementation this would return
    a SearchFlights use case backed by AmadeusSearchGateway.

    Here we use Travelpayouts instead.
    """
    return search_flights


def get_confirm_flight_price_use_case():
    """
    Tutorial-compatible dependency name.

    Travelpayouts does not require the same Amadeus-style
    flight-offer pricing confirmation flow, so the endpoint
    can remain available without pretending that Travelpayouts
    has the exact same API.
    """
    return search_flights


def get_create_flight_order_use_case(
    session: Session = Depends(get_session),
):
    """
    Tutorial-compatible dependency name.

    Returns the local order creator together with the DB session.
    """
    return create_order


def get_booking_details_use_case(
    session: Session = Depends(get_session),
):
    """
    Tutorial-compatible dependency name.

    Booking details are currently retrieved from our local DB.
    """
    return session


def get_cancel_booking_use_case(
    session: Session = Depends(get_session),
):
    """
    Tutorial-compatible dependency name.

    Travelpayouts is being used for flight search.
    Cancellation is therefore handled locally for now.
    """
    return session


def get_seat_map_use_case(
    session: Session = Depends(get_session),
):
    """
    Tutorial-compatible dependency name.

    Travelpayouts does not provide the same seat-map API
    used by the original Amadeus implementation.
    """
    return session


def get_seat_map_from_flight_offer_use_case():
    """
    Tutorial-compatible dependency name.

    Kept so the tutorial structure remains familiar.
    """
    return search_flights


def get_location_search_use_case():
    """
    Tutorial-compatible dependency name.

    Travelpayouts search is used as the external flight provider.
    """
    return search_flights


def get_travelled_destinations_use_case():
    """
    Tutorial-compatible dependency name.

    Travel analytics are not currently provided by Travelpayouts.
    """
    return None


def get_user_bookings_use_case(
    session: Session = Depends(get_session),
):
    """
    Tutorial-compatible dependency name.
    """
    return session


# ============================================================
# GET /shopping/flight-offers
# ============================================================
#
# IMPORTANT:
# This route is intentionally identical to the Nehemiah route.
#
# Original:
# @router.get("/shopping/flight-offers")
#
# Provider underneath:
# Travelpayouts
#
# ============================================================


@router.get("/shopping/flight-offers")
async def search_flights_get(
    request: Annotated[FlightSearch, Query()],
    search_flights_use_case=Depends(get_search_flights_use_case),
):
    """
    Search for flights.

    The route/function name follows the Nehemiah tutorial,
    while Travelpayouts is used underneath.
    """
    request_body = request.model_dump(exclude_none=True)
    print(request_body)
    # key, value
    key = f"flights:{json.dumps(request_body, sort_keys=True, default=str)}"
    print(key)
    cached_result = redis_cache.get(key)

    if cached_result:
        logger.info("Returning cached flight results")
        return cached_result
    try:
        # Travelpayouts provider call
        api_response = await search_flights_use_case(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            currency=request.currency,
            limit=request.limit,
        )

        if not api_response.get("success", False):
            raise HTTPException(
                status_code=502,
                detail="Travel provider failed",
            )

        flights = api_response.get("data", [])

        formatted = []

        for flight in flights:
            # ------------------------------------------------
            # Direct flight filter
            # ------------------------------------------------

            if request.direct_only and flight.get("transfers", 0) > 0:
                continue

            formatted.append(
                {
                    "flight_number": flight.get("flight_number"),
                    "airline": flight.get("airline"),
                    "origin": flight.get("origin"),
                    "destination": flight.get("destination"),
                    "departure_at": flight.get("departure_at"),
                    "duration": flight.get("duration"),
                    "transfers": flight.get(
                        "transfers",
                        0,
                    ),
                    "gate": flight.get("gate"),
                    "booking_link": flight.get("link"),
                    "price": flight.get("price"),
                }
            )

        # ----------------------------------------------------
        # Sorting
        # ----------------------------------------------------

        if request.sort_by == "price":
            formatted.sort(
                key=lambda x: (x["price"] if x["price"] is not None else 999999)
            )

        elif request.sort_by == "duration":
            formatted.sort(
                key=lambda x: (x["duration"] if x["duration"] is not None else 999999)
            )

        elif request.sort_by == "departure":
            formatted.sort(
                key=lambda x: (
                    x["departure_at"] if x["departure_at"] is not None else ""
                )
            )

        # ----------------------------------------------------
        # Return the same general structure used by the app
        # ----------------------------------------------------

        # return {
        #     "success": api_response.get("success"),
        #     "currency": api_response.get("currency"),
        #     "count": len(formatted),
        #     "flights": formatted,
        # }
        response = {
            "success": api_response.get("success"),
            "currency": api_response.get("currency"),
            "count": len(formatted),
            "flights": formatted,
        }

        redis_cache.set(
            key,
            response,
            expiration_seconds=300,
        )

        return response

    except HTTPException:
        raise

    except Exception:
        logger.exception("Flight search failed")

        raise HTTPException(
            status_code=500,
            detail=("An error occurred while searching for flights"),
        )


# ============================================================
# POST /shopping/flight-offers/pricing
# ============================================================
#
# KEEPING THE TUTORIAL ROUTE.
#
# Travelpayouts does not need to be forced into the exact
# Amadeus pricing-confirmation architecture.
#
# ============================================================


@router.post("/shopping/flight-offers/pricing")
async def confirm_price(
    request: FlightOffer,
    confirm_flight_price_use_case=Depends(get_confirm_flight_price_use_case),
):
    """
    Confirm flight pricing.

    Kept with the same tutorial route/function name.

    Travelpayouts search results are treated as the current
    price information rather than implementing the Amadeus
    Flight Offers Pricing API.
    """

    try:
        # If the selected flight already contains a price,
        # return it as the confirmed price.

        return {
            "success": True,
            "message": "Flight price confirmed",
            "data": request,
        }

    except Exception:
        logger.exception("Flight pricing confirmation failed")

        raise HTTPException(
            status_code=500,
            detail=("An error occurred while confirming flight pricing"),
        )


# ============================================================
# POST /booking/flight-orders
# ============================================================
#
# SAME ROUTE AS NEHEMIAH
#
# ============================================================


@router.post(
    "/booking/flight-orders",
    response_model=BookingResponse,
)
async def flight_order(
    request: FlightOrderRequest,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a FlyingBee flight booking.

    The selected flight and traveler information are stored
    together as a local booking.

    Travelpayouts provides the flight information and booking
    link. FlyingBee owns the local booking record.
    """

    logger.info(
        "Flight order creation initiated by user_id=%s",
        current_user.id,
    )

    try:
        # ----------------------------------------------------
        # 1. Create the flight order
        # ----------------------------------------------------

        order = FlightOrder(
            user_id=current_user.id,
            flight_number=request.flight_number,
            airline=request.airline,
            origin=request.origin,
            destination=request.destination,
            departure_at=request.departure_at,
            price=request.price,
            currency=request.currency,
            booking_link=request.booking_link,
            status="CREATED",
        )

        # ----------------------------------------------------
        # 2. Create traveler records
        # ----------------------------------------------------

        for traveler_data in request.travelers:
            traveler = Traveler(
                first_name=traveler_data.first_name,
                last_name=traveler_data.last_name,
                date_of_birth=traveler_data.date_of_birth,
                gender=traveler_data.gender,
                email=traveler_data.email,
                phone=traveler_data.phone,
                passport_number=traveler_data.passport_number,
                passport_expiry=traveler_data.passport_expiry,
                passport_country=traveler_data.passport_country,
            )

            order.travelers.append(traveler)

        # ----------------------------------------------------
        # 3. Save order + travelers
        # ----------------------------------------------------

        session.add(order)

        session.flush()

        # -----------------------------------------
        # 4. Create application Booking
        # -----------------------------------------

        booking = Booking(
            user_id=current_user.id,
            flight_order_id=order.id,
            status="CONFIRMED",
        )

        session.add(booking)

        # -----------------------------------------
        # 5. Commit everything together
        # -----------------------------------------

        session.commit()

        session.refresh(order)
        session.refresh(booking)

        logger.info(
            "Booking created successfully: user_id=%s booking_id=%s flight_order_id=%s",
            current_user.id,
            booking.id,
            order.id,
        )

        return BookingResponse(
            id=str(booking.id),
            flight_order_id=str(order.id),
            status=booking.status,
            message="Flight booking created successfully",
        )

    except Exception:
        session.rollback()

        logger.exception(
            "Flight booking creation failed for user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=500,
            detail=("An unexpected error occurred while creating the flight booking"),
        )

    #     session.commit()

    #     session.refresh(order)

    #     logger.info(
    #         "Flight order created successfully: %s",
    #         order.id,
    #     )

    #     # ----------------------------------------------------
    #     # 4. Return booking information
    #     # ----------------------------------------------------

    #     return FlightOrderResponse(
    #         order_id=str(order.id),
    #         status=order.status,
    #         message="Flight booking created successfully",
    #         travelers_count=len(order.travelers),
    #     )

    # except Exception:
    #     session.rollback()

    #     logger.exception(
    #         "Flight order creation failed",
    #     )

    #     raise HTTPException(
    #         status_code=500,
    #         detail="An unexpected error occurred while creating the flight booking",
    #     )


# ============================================================
# GET /shopping/seatmaps
# ============================================================
#
# SAME ROUTE AS NEHEMIAH
#
# Travelpayouts does not provide the same seat-map capability,
# so we keep the route for tutorial compatibility.
#
# ============================================================


@router.get("/shopping/seatmaps")
async def view_seat_map_get(
    flight_order_reference: Annotated[
        str,
        Query(alias="flightorderId"),
    ],
    session: Session = Depends(get_session),
):
    """
    Retrieve seat map.

    Travelpayouts does not expose the same Amadeus seat-map
    endpoint, so this remains a compatibility endpoint.
    """

    raise HTTPException(
        status_code=501,
        detail=(
            "Seat map retrieval is not currently "
            "supported by the Travelpayouts provider"
        ),
    )


# ============================================================
# POST /shopping/seatmaps
# ============================================================


@router.post("/shopping/seatmaps")
async def view_seat_map_post(
    request: dict,
):
    """
    Retrieve a seat map from a flight offer.

    Kept for compatibility with the Nehemiah API structure.
    """

    raise HTTPException(
        status_code=501,
        detail=(
            "Seat map retrieval is not currently "
            "supported by the Travelpayouts provider"
        ),
    )


# ============================================================
# GET /booking/flight-orders/{booking_id}
# ============================================================


@router.get("/booking/flight-orders/{booking_id}")
async def get_booking_details(
    booking_id: str,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get a booking including its traveler information.
    """

    try:
        from uuid import UUID

        from sqlmodel import select

        # ----------------------------------------------------
        # Validate booking ID
        # ----------------------------------------------------

        try:
            booking_uuid = UUID(booking_id)

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid booking ID format",
            )

        # ----------------------------------------------------
        # Get flight order
        # ----------------------------------------------------

        order = session.exec(
            select(FlightOrder).where(
                FlightOrder.id == booking_uuid,
                FlightOrder.user_id == current_user.id,
            )
        ).first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Booking not found",
            )

        # ----------------------------------------------------
        # Get travelers belonging to this order
        # ----------------------------------------------------

        travelers = session.exec(
            select(Traveler).where(Traveler.order_id == booking_uuid)
        ).all()

        # ----------------------------------------------------
        # Format travelers
        # ----------------------------------------------------

        traveler_data = [
            {
                "id": str(traveler.id),
                "first_name": traveler.first_name,
                "last_name": traveler.last_name,
                "date_of_birth": traveler.date_of_birth,
                "gender": traveler.gender,
                "email": traveler.email,
                "phone": traveler.phone,
                "passport_number": traveler.passport_number,
                "passport_expiry": traveler.passport_expiry,
                "passport_country": traveler.passport_country,
            }
            for traveler in travelers
        ]

        # ----------------------------------------------------
        # Return booking + travelers
        # ----------------------------------------------------

        return {
            "id": str(order.id),
            "flight_number": order.flight_number,
            "airline": order.airline,
            "origin": order.origin,
            "destination": order.destination,
            "departure_at": order.departure_at,
            "price": order.price,
            "currency": order.currency,
            "booking_link": order.booking_link,
            "status": order.status,
            "created_at": order.created_at,
            "travelers": traveler_data,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error fetching booking details")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving booking details",
        )


# ============================================================
# DELETE /booking/flight-orders/{booking_id}
# ============================================================


@router.delete("/booking/flight-orders/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Cancel a local booking.

    Travelpayouts is not being treated as an Amadeus-style
    order-management provider here.
    """

    try:
        from uuid import UUID
        from sqlmodel import select

        try:
            booking_uuid = UUID(booking_id)

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid booking ID format",
            )

        order = session.exec(
            select(FlightOrder).where(
                FlightOrder.id == booking_uuid,
                FlightOrder.user_id == current_user.id,
            )
        ).first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Booking not found",
            )

        if order.status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail=("This booking has already been cancelled"),
            )

        order.status = "CANCELLED"

        session.add(order)
        session.commit()
        session.refresh(order)

        return {
            "id": str(order.id),
            "status": order.status,
            "message": "Booking cancelled successfully",
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error cancelling booking")

        raise HTTPException(
            status_code=500,
            detail=("An error occurred while cancelling the booking"),
        )


# ============================================================
# GET /reference-data/locations
# ============================================================
#
# SAME TUTORIAL ROUTE
#
# ============================================================


@router.get("/reference-data/locations")
async def search_locations(
    keyword: str = Query(...),
):
    """
    Location search.

    Kept under the same route used by the tutorial.

    Implement the Travelpayouts location endpoint here when
    needed. For now, this keeps the API contract in place.
    """

    raise HTTPException(
        status_code=501,
        detail=(
            "Location search is not currently "
            "implemented for the Travelpayouts provider"
        ),
    )


# ============================================================
# GET /bookings
# ============================================================


@router.get("/bookings")
async def get_user_bookings(
    session: Session = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
    cursor: str | None = Query(
        None,
        description="Cursor for pagination",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description=("Maximum number of records to return"),
    ),
    include_count: bool = Query(
        False,
        description=("Include total_count in response"),
    ),
):
    """
    Get user's bookings.

    Kept with the same tutorial route.
    """

    try:
        from sqlmodel import select

        statement = (
            select(FlightOrder)
            .where(FlightOrder.user_id == current_user.id)
            .order_by(FlightOrder.id.desc())
            .limit(limit)
        )

        orders = session.exec(statement).all()

        items = [
            {
                "id": str(order.id),
                "pnr": None,
                "status": order.status,
                "created_at": getattr(
                    order,
                    "created_at",
                    None,
                ),
                "ticket_url": order.booking_link,
            }
            for order in orders
        ]

        return {
            "items": items,
            "next_cursor": None,
            "has_more": False,
            "has_previous": False,
            "total_count": (len(items) if include_count else None),
            "limit": limit,
        }

    except Exception:
        logger.exception("Error fetching bookings")

        raise HTTPException(
            status_code=500,
            detail=("An error occurred while fetching bookings"),
        )


# ============================================================
# GET /analytics/most-travelled-destinations
# ============================================================
#
# SAME TUTORIAL ROUTE
#
# ============================================================


@router.get("/analytics/most-travelled-destinations")
def get_most_travelled_destinations(
    origin_city_code: str,
    period: str,
):
    """
    Travel analytics endpoint.

    Travelpayouts is being used for flight search and does not
    provide the same Amadeus travel-analytics endpoint.

    Route is retained so the tutorial/frontend structure
    remains consistent.
    """

    raise HTTPException(
        status_code=501,
        detail=(
            "Travel analytics are not currently supported by the Travelpayouts provider"
        ),
    )


# from fastapi import APIRouter, Depends, HTTPException
# from sqlmodel import Session

# from backend.schemas.flights import FlightSearch
# from backend.external_services.travelpayouts import search_flights
# from backend.crud.database import get_session
# from backend.crud.flights import save_search

# from backend.schemas.orders import (
#     FlightOrderRequest,
#     FlightOrderResponse
# )

# from backend.models.orders import FlightOrder

# from backend.crud.orders import create_order

# # Future:
# # from backend.external_services.cache import redis_cache
# # from backend.utils.kafka import kafka_producer

# import logging

# logger = logging.getLogger(__name__)


# router = APIRouter(prefix="/api")


# # -------------------------------
# # Dependency Layer
# # -------------------------------

# def get_flight_search_provider():
#     return search_flights

# def get_order_creator():
#     return create_order


# # Future:
# # def get_cache():
# #     return redis_cache


# # def get_event_publisher():
# #     return kafka_producer


# # -------------------------------
# # Search Flights
# # -------------------------------

# @router.post("/flights/search")
# async def search(
#     request: FlightSearch,
#     session: Session = Depends(get_session),
#     flight_provider=Depends(get_flight_search_provider),
# ):

#     try:

#         # Save search history
#         save_search(
#             session,
#             request
#         )


#         # Future Redis caching
#         # cached_result = redis_cache.get(request)
#         # if cached_result:
#         #     return cached_result


#         api_response = await flight_provider(
#             origin=request.origin,
#             destination=request.destination,
#             departure_date=request.departure_date,
#             currency=request.currency,
#             limit=request.limit,
#         )


#         if not api_response.get("success", False):

#             raise HTTPException(
#                 status_code=502,
#                 detail="Travel provider failed"
#             )


#         flights = api_response.get(
#             "data",
#             []
#         )


#         formatted = []


#         for flight in flights:


#             # direct flight filter
#             if (
#                 request.direct_only
#                 and flight.get("transfers",0) > 0
#             ):
#                 continue


#             formatted.append(
#                 {
#                     "flight_number":
#                         flight.get("flight_number"),


#                     "airline":
#                         flight.get("airline"),


#                     "origin":
#                         flight.get("origin"),


#                     "destination":
#                         flight.get("destination"),


#                     "departure_at":
#                         flight.get("departure_at"),


#                     "duration":
#                         flight.get("duration"),


#                     "transfers":
#                         flight.get("transfers",0),


#                     "gate":
#                         flight.get("gate"),


#                     "booking_link":
#                         flight.get("link"),


#                     "price":
#                         flight.get("price"),
#                 }
#             )


#         # sorting

#         if request.sort_by == "price":

#             formatted.sort(
#                 key=lambda x:x["price"] or 999999
#             )


#         elif request.sort_by=="duration":

#             formatted.sort(
#                 key=lambda x:x["duration"] or 999999
#             )


#         elif request.sort_by=="departure":

#             formatted.sort(
#                 key=lambda x:x["departure_at"]
#             )


#         response = {

#             "success":
#                 api_response.get("success"),


#             "currency":
#                 api_response.get("currency"),


#             "count":
#                 len(formatted),


#             "flights":
#                 formatted
#         }


#         # Future Kafka event
#         #
#         # kafka_producer.publish(
#         #     "flight.search.completed",
#         #     response
#         # )


#         return response


#     except HTTPException:

#         raise


#     except Exception as e:

#         logger.exception(
#             "Flight search failed"
#         )

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )


# @router.get("/flights")
# async def get_flights():

#     return {
#         "message":"FlyingBee Flight API"
#     }

# # --------------------------------
# # Create Flight Order
# # --------------------------------

# @router.post(
#     "/flights/orders",
#     response_model=FlightOrderResponse
# )
# async def create_flight_order(
#     request: FlightOrderRequest,
#     session: Session = Depends(get_session),
# ):

#     try:

#         order = FlightOrder(

#             flight_number=request.flight_number,

#             airline=request.airline,

#             origin=request.origin,

#             destination=request.destination,

#             departure_at=request.departure_at,

#             price=request.price,

#             currency=request.currency,

#             booking_link=request.booking_link,

#             status="CREATED"
#         )


#         saved_order = create_order(
#             session,
#             order
#         )


#         # Future Kafka
#         #
#         # kafka_producer.publish(
#         #     "flight.order.created",
#         #     {
#         #        "order_id": str(saved_order.id)
#         #     }
#         # )


#         return {

#             "order_id":
#                 str(saved_order.id),

#             "status":
#                 saved_order.status,

#             "message":
#                 "Flight order created successfully"
#         }


#     except Exception as e:

#         logger.exception(
#             "Flight order creation failed"
#         )


#         raise HTTPException(

#             status_code=500,

#             detail=str(e)

#         )

# @router.post("/flights/price")
# async def confirm_price():
#         return ""
