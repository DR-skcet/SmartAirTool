import httpx
import logging
from fastapi import HTTPException
from app.services.amadeus_auth import get_amadeus_token
from app.utils.date_utils import generate_dates
from app.config import settings

# Get logger
logger = logging.getLogger(__name__)

async def search_flights(origin: str, destination: str, months: int):
    try:
        # Get authentication token
        logger.info(f"Getting Amadeus token for flight search from {origin} to {destination} for {months} months")
        token = await get_amadeus_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        all_flights = []  # Store all flights across all dates
        dates = generate_dates(months)
        logger.info(f"Generated {len(dates)} dates for search")
        
        async with httpx.AsyncClient() as client:
            for date in dates:
                params = {
                    "originLocationCode": origin,
                    "destinationLocationCode": destination,
                    "departureDate": date,
                    "adults": 1,
                    "nonStop": False,
                    "currencyCode": "USD",
                    "max": 10
                }
                url = f"{settings.AMADEUS_BASE_URL}/v2/shopping/flight-offers"
                try:
                    logger.info(f"Searching flights for date: {date}")
                    response = await client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    offers = data.get("data", [])
                    
                    if not offers:
                        logger.info(f"No flight offers found for date: {date}")
                        continue
                        
                    logger.info(f"Found {len(offers)} flight offers for date: {date}")
                    # Add date info to each flight offer and collect all flights
                    for offer in offers:
                        offer['search_date'] = date
                        all_flights.append(offer)
                except httpx.HTTPStatusError as e:
                    error_msg = f"API error for date {date}: {e.response.status_code}"
                    try:
                        error_details = e.response.json()
                        error_msg += f", Details: {error_details}"
                    except:
                        error_msg += f", Response: {e.response.text}"
                    logger.error(error_msg)
                    # Continue with other dates instead of failing completely
                except Exception as e:
                    logger.error(f"Failed on {date}: {str(e)}")
        
        if not all_flights:
            logger.warning("No flight results found for any of the dates")
            raise HTTPException(status_code=404, detail="No flights found for the specified criteria")
        
        # Find the overall cheapest and shortest flights
        def parse_duration(duration_str):
            """Parse duration string like 'PT9H20M' into total minutes"""
            duration_str = duration_str.replace("PT", "")
            hours = 0
            minutes = 0
            if "H" in duration_str:
                parts = duration_str.split("H")
                hours = int(parts[0])
                duration_str = parts[1] if len(parts) > 1 else ""
            if "M" in duration_str:
                minutes = int(duration_str.replace("M", ""))
            return hours * 60 + minutes
        
        cheapest_flight = min(all_flights, key=lambda x: float(x['price']['total']))
        shortest_flight = min(all_flights, key=lambda x: parse_duration(x['itineraries'][0]['duration']))
        
        results = {
            "total_flights_found": len(all_flights),
            "search_period": f"{months} months",
            "cheapest_flight": {
                "price": cheapest_flight['price']['total'],
                "currency": cheapest_flight['price']['currency'],
                "departure_date": cheapest_flight['search_date'],
                "duration": cheapest_flight['itineraries'][0]['duration'],
                "segments": len(cheapest_flight['itineraries'][0]['segments']),
                "airline": cheapest_flight['validatingAirlineCodes'][0],
                "full_details": cheapest_flight
            },
            "shortest_flight": {
                "duration": shortest_flight['itineraries'][0]['duration'],
                "price": shortest_flight['price']['total'],
                "currency": shortest_flight['price']['currency'],
                "departure_date": shortest_flight['search_date'],
                "segments": len(shortest_flight['itineraries'][0]['segments']),
                "airline": shortest_flight['validatingAirlineCodes'][0],
                "full_details": shortest_flight
            }
        }
        
        logger.info(f"Successfully processed {len(all_flights)} flights. Cheapest: {cheapest_flight['price']['total']} {cheapest_flight['price']['currency']}, Shortest: {shortest_flight['itineraries'][0]['duration']}")
        return results
        
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_flights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during flight search")

