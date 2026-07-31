from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.schemas.flights import FlightSearch
from backend.external_services.travelpayouts import search_flights
from backend.crud.database import get_session
from backend.crud.flights import save_search

router = APIRouter(prefix="/api")


@router.get("/flights")
async def get_flights():
    return {"message": "Flights"}


@router.post("/flights/search")
async def search(
    request: FlightSearch,
    session: Session = Depends(get_session),
):
    save_search(session, request)

    api_response = await search_flights(
        origin=request.origin,
        destination=request.destination,
        departure_date=request.departure_date,
        currency=request.currency,
        limit=request.limit,
    )

    flights = api_response.get("data", [])

    formatted = []

    for flight in flights:
        # Skip connecting flights if user requested direct only
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
                "transfers": flight.get("transfers"),
                "gate": flight.get("gate"),
                "booking_link": flight.get("link"),
                "price": flight.get("price"),
            }
        )

    if request.sort_by == "price":
        formatted.sort(key=lambda x: x["price"])

    elif request.sort_by == "duration":
        formatted.sort(key=lambda x: x["duration"])

    elif request.sort_by == "departure":
        formatted.sort(key=lambda x: x["departure_at"])

    return {
        "success": api_response.get("success"),
        "currency": api_response.get("currency"),
        "count": len(formatted),
        "flights": formatted,
    }
