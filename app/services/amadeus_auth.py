import httpx
from app.config import settings

_token_cache = {}

async def get_amadeus_token():
    if _token_cache.get("token"):
        return _token_cache["token"]

    url = f"{settings.AMADEUS_BASE_URL}/v1/security/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': settings.AMADEUS_CLIENT_ID,
        'client_secret': settings.AMADEUS_CLIENT_SECRET
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        token = response.json()['access_token']
        _token_cache["token"] = token
        return token
