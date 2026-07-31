import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field


class FlightSearchHistory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    origin: str
    destination: str

    departure_date: str
    return_date: str | None = None

    adults: int = 1
    children: int = 0
    infants: int = 0

    cabin_class: str = "economy"

    currency: str = "USD"

    searched_at: datetime = Field(default_factory=datetime.utcnow)

    direct_only: bool = False

    sort_by: str = "price"

    limit: int = 20
