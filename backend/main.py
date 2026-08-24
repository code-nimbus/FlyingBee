from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.crud.database import init_db
from backend.routers import flights, users

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(users.router)
app.include_router(flights.router)


@app.get("/")
def hello():
    return {"message": "Flight Booking API"}


class Person: ...


john = Person()
