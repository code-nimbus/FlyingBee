from sqlmodel import Session

from backend.models.orders import FlightOrder, Traveler


def create_order(
    session: Session,
    order: FlightOrder,
    travelers: list[dict],
) -> FlightOrder:
    session.add(order)

    session.flush()

    for traveler_data in travelers:
        traveler = Traveler(
            order_id=order.id,
            **traveler_data,
        )

        session.add(traveler)

    session.commit()

    session.refresh(order)

    return order
