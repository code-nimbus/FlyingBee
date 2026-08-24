from uuid import UUID

from backend.application.bookings.get_user_bookings import (
    BookingListItemRecord,
    UserBookingsPage,
)
from backend.models.booking import Booking
from backend.utils.pagination import CursorPaginator
from sqlmodel import Session, select


class SqlModelBookingRepository:
    """
    SQLModel repository for Booking persistence.

    Keeps database operations out of the FastAPI router.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(
        self,
        booking_id: UUID,
        user_id: UUID,
    ) -> Booking | None:
        statement = select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[Booking]:
        statement = select(Booking).where(Booking.user_id == user_id)

        return list(self.session.exec(statement).all())

    def get_all(self) -> list[Booking]:
        statement = select(Booking)

        return list(self.session.exec(statement).all())

    def get_by_flight_order_id(
        self,
        *,
        flight_order_id: str,
        user_id: UUID,
    ) -> Booking | None:
        statement = select(Booking).where(
            Booking.flight_order_id == flight_order_id,
            Booking.user_id == user_id,
        )

        return self.session.exec(statement).first()

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
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return booking

    def get_user_booking_details(
        self,
        booking_id: UUID,
        user_id: UUID,
    ) -> Booking | None:
        statement = select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )

        return self.session.exec(statement).first()

    def get_user_bookings(
        self,
        *,
        user_id: UUID,
        cursor: str | None,
        limit: int,
        include_count: bool,
    ) -> UserBookingsPage:
        """
        Return a cursor-paginated list of bookings belonging
        to the authenticated user.
        """

        paginator = CursorPaginator(
            cursor=cursor,
            limit=limit,
            order_fields=["created_at", "id"],
            order_direction="desc",
        )

        statement = select(Booking).where(Booking.user_id == user_id)

        # Apply cursor/keyset filtering.
        statement = paginator.apply_cursor_filter(
            statement,
            Booking,
        )

        # Apply deterministic ordering.
        statement = paginator.apply_ordering(
            statement,
            Booking,
        )

        # Fetch limit + 1 so we can determine has_more.
        statement = paginator.apply_limit(statement)

        bookings = list(self.session.exec(statement).all())

        # Optional total count.
        total_count = None

        if include_count:
            from sqlalchemy import func

            count_statement = (
                select(func.count())
                .select_from(Booking)
                .where(Booking.user_id == user_id)
            )

            total_count = self.session.exec(count_statement).one()

        # Convert to pagination result.
        bookings, next_cursor, has_more = paginator.build_result(
            bookings,
            lambda booking: {
                "created_at": booking.created_at,
                "id": booking.id,
            },
        )

        items = [
            BookingListItemRecord(
                id=booking.id,
                # pnr=booking.pnr,
                status=booking.status,
                created_at=booking.created_at,
                ticket_url=booking.ticket_url,
            )
            for booking in bookings
        ]

        return UserBookingsPage(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
            has_previous=cursor is not None,
            total_count=total_count,
            limit=paginator.limit,
        )


# from uuid import UUID

# from sqlmodel import Session, select

# # Change this import if your Booking model lives somewhere else.
# from backend.models.booking import Booking


# class SqlModelBookingRepository:
#     """
#     SQLModel repository for Booking persistence.

#     Keeps database operations out of the FastAPI router.
#     """

#     def __init__(self, session: Session):
#         self.session = session

#     def get_by_id(self, booking_id: UUID, user_id: UUID,) -> Booking | None:
#         statement = select(Booking).where(
#             Booking.id == booking_id,
#             Booking.user_id == user_id,
#         )
#         return self.session.exec(statement).first()

#     def get_by_user_id(self, user_id: int) -> list[Booking]:
#         statement = select(Booking).where(Booking.user_id == user_id)

#         return list(self.session.exec(statement).all())

#     def get_all(self) -> list[Booking]:
#         statement = select(Booking)
#         return list(self.session.exec(statement).all())

#     def get_by_flight_order_id(
#         self,
#         *,
#         flight_order_id: str,
#         user_id: UUID,
#     ) -> Booking | None:
#         """
#         Find a booking by Duffel flight order ID and verify
#         that it belongs to the authenticated user.
#         """
#         statement = select(Booking).where(
#             Booking.flight_order_id == flight_order_id,
#             Booking.user_id == user_id,
#         )

#         return self.session.exec(statement).first()

#     def create(self, booking: Booking) -> Booking:
#         self.session.add(booking)
#         self.session.commit()
#         self.session.refresh(booking)

#         return booking

#     def update(self, booking: Booking) -> Booking:
#         self.session.add(booking)
#         self.session.commit()
#         self.session.refresh(booking)

#         return booking

#     def delete(self, booking: Booking) -> None:
#         self.session.delete(booking)
#         self.session.commit()

#     def save(self, booking: Booking) -> Booking:
#         """
#         Save a booking whether it is new or already exists.
#         """
#         self.session.add(booking)
#         self.session.commit()
#         self.session.refresh(booking)

#         return booking

#     def get_user_booking_details(
#         self,
#         booking_id: UUID,
#         user_id: UUID,
#     ) -> Booking | None:
#         """
#         Get a booking by its database ID while ensuring that
#         the booking belongs to the authenticated user.

#         This method is used by GetBookingDetails.
#         """
#         statement = select(Booking).where(
#             Booking.id == booking_id,
#             Booking.user_id == user_id,
#         )

#         return self.session.exec(statement).first()
