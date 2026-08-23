from sqlmodel import Session, select

# Change this import if your Booking model lives somewhere else.
from backend.models.booking import Booking


class SqlModelBookingRepository:
    """
    SQLModel repository for Booking persistence.

    Keeps database operations out of the FastAPI router.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, booking_id: int) -> Booking | None:
        statement = select(Booking).where(Booking.id == booking_id)
        return self.session.exec(statement).first()

    def get_by_user_id(self, user_id: int) -> list[Booking]:
        statement = select(Booking).where(Booking.user_id == user_id)

        return list(self.session.exec(statement).all())

    def get_all(self) -> list[Booking]:
        statement = select(Booking)
        return list(self.session.exec(statement).all())

    def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return booking

    def update(self, booking: Booking) -> Booking:
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return booking

    def delete(self, booking: Booking) -> None:
        self.session.delete(booking)
        self.session.commit()

    def save(self, booking: Booking) -> Booking:
        """
        Save a booking whether it is new or already exists.
        """
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return booking
