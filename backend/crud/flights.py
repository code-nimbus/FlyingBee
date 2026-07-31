from backend.models.flights import FlightSearchHistory


def save_search(session, request):
    history = FlightSearchHistory(
        origin=request.origin,
        destination=request.destination,
        departure_date=request.departure_date,
        return_date=request.return_date,
        adults=request.adults,
        children=request.children,
        infants=request.infants,
        cabin_class=request.cabin_class,
        currency=request.currency,
    )
    session.add(history)
    session.commit()
    session.refresh(history)

    return history
