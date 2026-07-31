import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TRAVELPAYOUTS_API_KEY")
BASE_URL = os.getenv("TRAVELPAYOUTS_BASE_URL")


async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    currency: str,
    limit: int,
):
    url = f"{BASE_URL}/aviasales/v3/prices_for_dates"

    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_date,
        "currency": currency,
        "sorting": "price",
        "limit": limit,
        "token": API_KEY,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        return {
            "success": False,
            "error": response.text,
        }

    return response.json()
