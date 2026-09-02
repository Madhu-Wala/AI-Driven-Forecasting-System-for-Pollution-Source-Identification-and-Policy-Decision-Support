import os
import httpx
from dotenv import load_dotenv
from app.utils.cache import get_cache, set_cache

load_dotenv()

GOOGLE_AIR_QUALITY_API_KEY = os.getenv("GOOGLE_AIR_QUALITY_API_KEY")

CURRENT_URL = (
    "https://airquality.googleapis.com/v1/"
    "currentConditions:lookup"
)

FORECAST_URL = (
    "https://airquality.googleapis.com/v1/"
    "forecast:lookup"
)


async def get_current_air_quality(latitude: float, longitude: float):

    if not GOOGLE_AIR_QUALITY_API_KEY:
        raise RuntimeError(
            "Google Air Quality API key is not configured"
        )

    # Round coordinates so nearby requests share the same cache.
    latitude = round(float(latitude), 3)
    longitude = round(float(longitude), 3)

    cache_key = f"google_aq:{latitude}:{longitude}"

    # Check cache first.
    cached_data = get_cache(cache_key)

    if cached_data is not None:
        print(
            f"Google AQ cache HIT: {latitude}, {longitude}"
        )
        return cached_data

    print(
        f"Google AQ cache MISS: {latitude}, {longitude}"
    )

    params = {
        "key": GOOGLE_AIR_QUALITY_API_KEY
    }

    payload = {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "universalAqi": True,
        "extraComputations": [
            "POLLUTANT_CONCENTRATION",
            "LOCAL_AQI",
            "DOMINANT_POLLUTANT_CONCENTRATION",
            "POLLUTANT_ADDITIONAL_INFO"
        ],
        "languageCode": "en"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            CURRENT_URL,
            params=params,
            json=payload
        )

    response.raise_for_status()

    data = response.json()

    # Cache Google response for 15 minutes.
    set_cache(
        cache_key,
        data,
        ttl_seconds=15 * 60
    )

    return data

from datetime import datetime, timedelta, timezone

async def get_air_quality_forecast(
    latitude: float,
    longitude: float,
    hours: int = 48
):
    if not GOOGLE_AIR_QUALITY_API_KEY:
        raise RuntimeError("Google Air Quality API key is not configured")

    # Google supports up to 96 hours
    hours = min(hours, 96)

    now = datetime.now(timezone.utc)

    # Start from the next hour
    start_time = now.replace(
        minute=0,
        second=0,
        microsecond=0
    ) + timedelta(hours=1)

    end_time = start_time + timedelta(hours=hours)

    params = {
        "key": GOOGLE_AIR_QUALITY_API_KEY
    }

    payload = {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "universalAqi": True,

        "period": {
            "startTime": start_time.isoformat().replace("+00:00", "Z"),
            "endTime": end_time.isoformat().replace("+00:00", "Z")
        },

        "languageCode": "en",

        "extraComputations": [
            "LOCAL_AQI",
            "POLLUTANT_CONCENTRATION",
            "DOMINANT_POLLUTANT_CONCENTRATION"
        ],

        "pageSize": hours
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            FORECAST_URL,
            params=params,
            json=payload
        )

    if response.status_code != 200:
        print("Google forecast error:")
        print(response.text)

    response.raise_for_status()

    return response.json()