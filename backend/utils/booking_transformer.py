"""
Utility functions for transforming Duffel booking data into
frontend-friendly booking response data.
"""

from datetime import datetime
from typing import Any


def transform_duffel_to_booking_success(
    booking_id: str,
    booking_date: datetime,
    booking_status: str,
    flight_order_id: str,
    user_email: str | None = None,
) -> dict[str, Any]:
    """
    Transform database booking information into the format expected
    by the frontend booking success/details page.

    The current Booking model stores the Duffel order ID rather than
    the complete Duffel order response.

    Args:
        booking_id:
            Database booking ID.

        booking_date:
            Date/time when the booking was created.

        booking_status:
            Current booking status.

        flight_order_id:
            Duffel flight order ID.

        user_email:
            Email address of the logged-in user.

    Returns:
        A frontend-friendly booking response dictionary.
    """

    return {
        "orderId": booking_id,
        "pnr": "N/A",
        "bookingDate": _format_datetime(booking_date),
        "status": booking_status,
        "flightDetails": {},
        "passengers": [],
        "pricing": {
            "total": "0.00",
            "currency": "USD",
            "breakdown": [],
        },
        "contact": {
            "name": "N/A",
            "email": user_email or "N/A",
            "phone": "N/A",
        },
        "flightOrderId": flight_order_id,
        "ticket_url": None,
    }


def _format_datetime(value: datetime | None) -> str:
    """
    Convert a datetime to the ISO format expected by the frontend.
    """

    if value is None:
        return ""

    return value.isoformat().replace("+00:00", "Z")


def transform_duffel_order_to_booking_success(
    *,
    booking_id: str,
    booking_date: datetime,
    booking_status: str,
    flight_order_id: str,
    duffel_order: dict[str, Any],
    user_email: str | None = None,
) -> dict[str, Any]:
    """
    Transform a complete Duffel order response into the frontend
    booking success format.

    This function is useful when the Duffel API order response is
    available.

    Args:
        booking_id:
            Database booking ID.

        booking_date:
            Booking creation timestamp.

        booking_status:
            Current database booking status.

        flight_order_id:
            Duffel order ID.

        duffel_order:
            Raw Duffel order response.

        user_email:
            Logged-in user's email.

    Returns:
        Frontend-friendly booking response.
    """

    return {
        "orderId": booking_id,
        "pnr": _extract_pnr(duffel_order),
        "bookingDate": _format_datetime(booking_date),
        "status": booking_status,
        "flightDetails": _transform_flight_details(duffel_order),
        "passengers": _transform_passengers(duffel_order),
        "pricing": _transform_pricing(duffel_order),
        "contact": _transform_contact(
            duffel_order,
            user_email=user_email,
        ),
        "flightOrderId": flight_order_id,
        "ticket_url": _extract_ticket_url(duffel_order),
    }


def _extract_pnr(duffel_order: dict[str, Any]) -> str:
    """
    Extract the booking reference / PNR from a Duffel order.

    Duffel commonly exposes the booking reference as `booking_reference`.
    """

    return (
        duffel_order.get("booking_reference")
        or duffel_order.get("bookingReference")
        or "N/A"
    )


def _extract_ticket_url(duffel_order: dict[str, Any]) -> str | None:
    """
    Extract a ticket URL if one exists in the Duffel response.

    Not every Duffel order contains a ticket URL, so None is returned
    when it is unavailable.
    """

    return duffel_order.get("ticket_url") or duffel_order.get("ticketUrl")


def _transform_flight_details(
    duffel_order: dict[str, Any],
) -> dict[str, Any]:
    """
    Transform Duffel slices and segments into the frontend format.

    Duffel structure:

        order
          └── slices
                └── segments
    """

    slices = duffel_order.get("slices", [])

    result: dict[str, Any] = {}

    if len(slices) > 0:
        result["outbound"] = _transform_slice(slices[0])

    if len(slices) > 1:
        result["return"] = _transform_slice(slices[1])

    return result


def _transform_slice(
    flight_slice: dict[str, Any],
) -> dict[str, Any]:
    """
    Transform one Duffel slice.
    """

    segments = flight_slice.get("segments", [])

    if not segments:
        return {
            "date": "",
            "segments": [],
        }

    first_segment = segments[0]

    departure = first_segment.get("departing_at", "")

    date = ""

    if departure:
        date = departure.split("T")[0]

    transformed_segments = []

    for segment in segments:
        departing_at = segment.get("departing_at", "")
        arriving_at = segment.get("arriving_at", "")

        departure_time = _extract_time(departing_at)
        arrival_time = _extract_time(arriving_at)

        origin = segment.get("origin", {}) or {}
        destination = segment.get("destination", {}) or {}

        operating_carrier = (
            segment.get(
                "operating_carrier",
                {},
            )
            or {}
        )

        marketing_carrier = (
            segment.get(
                "marketing_carrier",
                {},
            )
            or {}
        )

        carrier_code = (
            marketing_carrier.get("iata_code")
            or operating_carrier.get("iata_code")
            or ""
        )

        flight_number = (
            segment.get("marketing_carrier_flight_number")
            or segment.get("operating_carrier_flight_number")
            or ""
        )

        flight = f"{carrier_code}{flight_number}"

        duration = segment.get("duration", "")
        duration_str = _format_duration(duration)

        transformed_segments.append(
            {
                "departure": {
                    "airport": origin.get("iata_code", ""),
                    "time": departure_time,
                    "terminal": origin.get("terminal"),
                },
                "arrival": {
                    "airport": destination.get("iata_code", ""),
                    "time": arrival_time,
                    "terminal": destination.get("terminal"),
                },
                "flight": flight,
                "duration": duration_str,
            }
        )

    return {
        "date": date,
        "segments": transformed_segments,
    }


def _extract_time(datetime_value: str | None) -> str:
    """
    Convert an ISO datetime such as:

        2026-08-25T10:30:00

    into:

        10:30
    """

    if not datetime_value:
        return ""

    if "T" not in datetime_value:
        return ""

    time_part = datetime_value.split("T", 1)[1]

    return time_part[:5]


def _format_duration(duration: str | None) -> str:
    """
    Convert Duffel duration into a human-readable duration.

    Example:

        PT2H30M -> 2h 30m
    """

    if not duration:
        return "0h 0m"

    duration = duration.strip()

    if not duration.startswith("PT"):
        return duration

    duration = duration[2:]

    hours = 0
    minutes = 0

    current_number = ""

    for character in duration:
        if character.isdigit():
            current_number += character
            continue

        if character == "H":
            if current_number:
                hours = int(current_number)

            current_number = ""

        elif character == "M":
            if current_number:
                minutes = int(current_number)

            current_number = ""

    return f"{hours}h {minutes}m"


def _transform_passengers(
    duffel_order: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Transform Duffel passengers into the frontend passenger format.
    """

    passengers = []

    for passenger in duffel_order.get("passengers", []):
        passenger_id = passenger.get("id") or passenger.get("passenger_id") or ""

        passenger_type = _map_passenger_type(
            passenger.get("type") or passenger.get("passenger_type") or "adult"
        )

        given_name = passenger.get("given_name") or passenger.get("first_name") or ""

        family_name = passenger.get("family_name") or passenger.get("last_name") or ""

        name = f"{given_name} {family_name}".strip()

        passengers.append(
            {
                "id": passenger_id,
                "type": passenger_type,
                "name": name,
                "seat": _extract_passenger_seat(passenger),
            }
        )

    return passengers


def _map_passenger_type(passenger_type: str) -> str:
    """
    Convert Duffel passenger types into frontend labels.
    """

    type_map = {
        "adult": "Adult",
        "child": "Child",
        "infant_without_seat": "Infant",
        "infant_with_seat": "Infant",
    }

    return type_map.get(
        passenger_type.lower(),
        "Adult",
    )


def _extract_passenger_seat(
    passenger: dict[str, Any],
) -> str | None:
    """
    Try to extract seat information when available.

    Duffel seat information may be represented differently depending
    on the order/seat selection flow.
    """

    seat = passenger.get("seat")

    if isinstance(seat, str):
        return seat

    if isinstance(seat, dict):
        return seat.get("designator") or seat.get("seat_number") or seat.get("number")

    return None


def _transform_pricing(
    duffel_order: dict[str, Any],
) -> dict[str, Any]:
    """
    Transform Duffel order pricing into frontend format.
    """

    total_amount = "0.00"
    currency = "USD"

    total = duffel_order.get("total_amount")

    if total is not None:
        total_amount = str(total)

    if duffel_order.get("total_currency"):
        currency = str(duffel_order["total_currency"])

    breakdown = []

    base_amount = duffel_order.get("base_amount")

    base_currency = duffel_order.get(
        "base_currency",
        currency,
    )

    if base_amount is not None:
        breakdown.append(
            {
                "item": "Base Fare",
                "amount": str(base_amount),
                "currency": base_currency,
            }
        )

    tax_amount = duffel_order.get("tax_amount")

    tax_currency = duffel_order.get(
        "tax_currency",
        currency,
    )

    if tax_amount is not None:
        try:
            if float(tax_amount) > 0:
                breakdown.append(
                    {
                        "item": "Taxes",
                        "amount": str(tax_amount),
                        "currency": tax_currency,
                    }
                )
        except (TypeError, ValueError):
            breakdown.append(
                {
                    "item": "Taxes",
                    "amount": str(tax_amount),
                    "currency": tax_currency,
                }
            )

    return {
        "total": total_amount,
        "currency": currency,
        "breakdown": breakdown,
    }


def _transform_contact(
    duffel_order: dict[str, Any],
    user_email: str | None = None,
) -> dict[str, Any]:
    """
    Extract contact information from the Duffel order.

    Uses the authenticated user's email as the fallback.
    """

    passengers = duffel_order.get(
        "passengers",
        [],
    )

    contact = (
        duffel_order.get(
            "contact",
            {},
        )
        or {}
    )

    email = contact.get("email") or contact.get("email_address") or user_email or "N/A"

    phone = contact.get("phone") or contact.get("phone_number") or "N/A"

    name = contact.get("name") or "N/A"

    if name == "N/A" and passengers:
        first_passenger = passengers[0]

        given_name = first_passenger.get("given_name") or ""

        family_name = first_passenger.get("family_name") or ""

        passenger_name = (f"{given_name} {family_name}").strip()

        if passenger_name:
            name = passenger_name

    return {
        "name": name,
        "email": email,
        "phone": phone,
    }
