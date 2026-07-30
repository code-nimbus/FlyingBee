# def main():
#     print("Hello from backend")


# if __name__=="__main__":
#     main()
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "Flight Booking API"}
