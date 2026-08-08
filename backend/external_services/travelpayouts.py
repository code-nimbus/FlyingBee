import os

import httpx
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(dotenv_path=env_path)


API_KEY = os.getenv("TRAVELPAYOUTS_API_KEY")
BASE_URL = os.getenv("TRAVELPAYOUTS_BASE_URL")


async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    currency: str,
    limit: int,
):
    """
    Search flights using the Travelpayouts / Aviasales API.

    This function is the Travelpayouts implementation behind
    the tutorial's SearchFlights functionality.
    """

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
        response = await client.get(
            url,
            params=params,
        )

    if response.status_code != 200:
        return {
            "success": False,
            "error": response.text,
        }

    data = response.json()

    return {
        "success": True,
        **data,
    }


# import os
# import httpx

# from pathlib import Path
# from dotenv import load_dotenv


# env_path = (
#     Path(__file__)
#     .resolve()
#     .parents[1]
#     / ".env"
# )


# load_dotenv(
#     dotenv_path=env_path
# )


# API_KEY=os.getenv(
#     "TRAVELPAYOUTS_API_KEY"
# )


# BASE_URL=os.getenv(
#     "TRAVELPAYOUTS_BASE_URL"
# )


# async def search_flights(
#     origin:str,
#     destination:str,
#     departure_date:str,
#     currency:str,
#     limit:int
# ):


#     url=f"{BASE_URL}/aviasales/v3/prices_for_dates"


#     params={

#         "origin":origin,

#         "destination":destination,

#         "departure_at":departure_date,

#         "currency":currency,

#         "limit":limit,

#         "sorting":"price",

#         "token":API_KEY

#     }


#     async with httpx.AsyncClient(
#         timeout=30
#     ) as client:


#         response=await client.get(
#             url,
#             params=params
#         )

#     if response.status_code != 200:

#         return {

#             "success":False,

#             "error":response.text

#         }


#     data = response.json()

#     return {

#         "success":True,

#         **data
#     }

# # import os
# # import httpx
# # from dotenv import load_dotenv

# # load_dotenv()

# # API_KEY = os.getenv("TRAVELPAYOUTS_API_KEY")
# # BASE_URL = os.getenv("TRAVELPAYOUTS_BASE_URL")


# # async def search_flights(
# #     origin: str,
# #     destination: str,
# #     departure_date: str,
# #     currency: str,
# #     limit: int,
# # ):
# #     url = f"{BASE_URL}/aviasales/v3/prices_for_dates"

# #     params = {
# #         "origin": origin,
# #         "destination": destination,
# #         "departure_at": departure_date,
# #         "currency": currency,
# #         "sorting": "price",
# #         "limit": limit,
# #         "token": API_KEY,
# #     }

# #     async with httpx.AsyncClient(timeout=30) as client:
# #         response = await client.get(url, params=params)

# #     if response.status_code != 200:
# #         return {
# #             "success": False,
# #             "error": response.text,
# #         }

# #     return response.json()
