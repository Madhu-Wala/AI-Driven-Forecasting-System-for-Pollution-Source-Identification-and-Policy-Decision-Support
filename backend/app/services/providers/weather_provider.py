import requests
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import time

OPEN_METEO_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)

IST = ZoneInfo("Asia/Kolkata")

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_FIELDS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
    "wind_speed_10m_mean",
    "wind_direction_10m_dominant",
    "pressure_msl_mean",
    "precipitation_sum"
]


def get_weather_forecast(latitude, longitude, forecast_days=2):
    """
    Fetch weather forecast from Open-Meteo
    for the given latitude and longitude.

    Returns:
        list of daily weather records.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": forecast_days,
        "daily": ",".join(WEATHER_FIELDS),
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "daily" not in data:
        raise RuntimeError(
            "Open-Meteo response does not contain daily weather data."
        )

    daily = data["daily"]

    dates = daily.get("time", [])

    if not dates:
        raise RuntimeError(
            "Open-Meteo returned no forecast dates."
        )

    weather_records = []

    for i, date in enumerate(dates):

        record = {
            "date": date
        }

        for field in WEATHER_FIELDS:
            values = daily.get(field, [])

            record[field] = (
                values[i]
                if i < len(values)
                else None
            )

        weather_records.append(record)

    return weather_records

# ============================================================
# Hourly Weather - Source Identification Only
# ============================================================

HOURLY_WEATHER_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "pressure_msl",
]


def get_hourly_weather_record(
    latitude,
    longitude,
    target_timestamp
):
    """
    Fetch hourly weather matching the pollution observation hour.

    This function is separate from the existing daily
    weather forecast used by the prediction pipeline.
    """

    if isinstance(target_timestamp, str):
        target_timestamp = datetime.fromisoformat(
            target_timestamp.replace("Z", "+00:00")
        )

    if target_timestamp.tzinfo is not None:
        target_timestamp = target_timestamp.astimezone(IST)
    else:
        target_timestamp = target_timestamp.replace(tzinfo=IST)

    target_timestamp = target_timestamp.replace(
        minute=0,
        second=0,
        microsecond=0
    )

    target_hour = target_timestamp.strftime("%Y-%m-%dT%H:%M")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_WEATHER_FIELDS),
        "timezone": "Asia/Kolkata",
        "past_days": 1,
        "forecast_days": 2,
    }

    response = None

    for attempt in range(3):
        try:
            response = requests.get(
                OPEN_METEO_URL,
                params=params,
                timeout=20
            )
            response.raise_for_status()
            break

        except requests.RequestException:
            if attempt == 2:
                raise

            time.sleep(2 * (attempt + 1))

    data = response.json()

    if "hourly" not in data:
        raise RuntimeError(
            "Open-Meteo response does not contain hourly weather data."
        )

    hourly = data["hourly"]
    timestamps = hourly.get("time", [])

    if target_hour not in timestamps:
        raise RuntimeError(
            f"Weather data unavailable for observation hour: {target_hour}"
        )

    index = timestamps.index(target_hour)

    record = {
        "date": target_hour
    }

    for field in HOURLY_WEATHER_FIELDS:
        values = hourly.get(field, [])

        record[field] = (
            values[index]
            if index < len(values)
            else None
        )

    return record


# Keep the function name expected by source_identification_service.py.
def get_weather_for_date(
    latitude,
    longitude,
    target_timestamp
):
    return get_hourly_weather_record(
        latitude=latitude,
        longitude=longitude,
        target_timestamp=target_timestamp
    )