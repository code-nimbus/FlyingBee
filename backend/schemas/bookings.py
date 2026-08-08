from pydantic import BaseModel


class BookingResponse(BaseModel):
    id: str
    flight_order_id: str
    status: str
    message: str
