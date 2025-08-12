from pydantic import BaseModel

class FlightRequest(BaseModel):
    origin: str
    destination: str
    months: int = 3

class FlightOption(BaseModel):
    price: float
    duration: str
    departure_date: str
    airline: str