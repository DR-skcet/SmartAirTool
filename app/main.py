from fastapi import FastAPI, Query
from app.services.flight_search import search_flights

app = FastAPI()

@app.get("/search")
async def search(
    origin: str = Query(..., min_length=3, max_length=3),
    destination: str = Query(..., min_length=3, max_length=3),
    months: int = Query(3, ge=1, le=6)
):
    return await search_flights(origin, destination, months)
