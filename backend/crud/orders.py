from sqlmodel import Session

from backend.models.orders import FlightOrder


def create_order(session: Session, order: FlightOrder):
    session.add(order)

    session.commit()

    session.refresh(order)

    return order
