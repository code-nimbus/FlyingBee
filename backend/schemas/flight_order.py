from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


class IdentityDocument(BaseModel):
    type: Literal["passport"] = "passport"
    unique_identifier: str = Field(min_length=1, max_length=15)
    issuing_country_code: str = Field(min_length=2, max_length=2)
    expires_on: date


# class FlightOrderPassenger(BaseModel):
#     id: str | None = None

#     type: Literal["adult", "child", "infant"] = "adult"

#     title: Literal["mr", "mrs", "ms", "miss", "dr"] | None = None

#     given_name: str = Field(min_length=1, max_length=20)
#     family_name: str = Field(min_length=1, max_length=20)

#     gender: Literal["m", "f"] | None = None

#     born_on: date

#     email: EmailStr
#     phone_number: str

#     # Optional passport information
#     identity_documents: list[dict] | None = None


class FlightOrderPassenger(BaseModel):
    id: str | None = None

    type: Literal["adult", "child", "infant"] = "adult"

    title: Literal["mr", "mrs", "ms", "miss", "dr"] | None = None

    given_name: str = Field(min_length=1, max_length=20)
    family_name: str = Field(min_length=1, max_length=20)

    gender: Literal["m", "f"] | None = None

    born_on: date

    email: EmailStr
    phone_number: str

    identity_documents: list[IdentityDocument] | None = None


# class FlightOrderRequestBody(BaseModel):
#     offer_id: str = Field(min_length=1)

#     passengers: list[FlightOrderPassenger] = Field(min_length=1)

#     # Start with hold so you don't need payment integration yet.
#     type: Literal["hold", "instant"] = "hold"

#     # Required only for instant orders.
#     payments: list[dict] | None = None

#     # Optional Duffel user IDs.
#     users: list[str] | None = None

#     # Optional services such as seats/bags.
#     services: list[dict] | None = None

#     metadata: dict | None = None


class FlightOrderRequestBody(BaseModel):
    offer_id: str = Field(min_length=1)

    passengers: list[FlightOrderPassenger] = Field(min_length=1)

    type: Literal["hold", "instant"] = "hold"

    payments: list[dict] | None = None

    users: list[str] | None = None

    # services: list[dict] | None = None

    # metadata: dict | None = None

    @model_validator(mode="after")
    def validate_order_type(self):
        if self.type == "hold" and self.payments:
            raise ValueError("payments must be omitted for hold orders")

        if self.type == "instant" and not self.payments:
            raise ValueError("payments are required for instant orders")

        return self
