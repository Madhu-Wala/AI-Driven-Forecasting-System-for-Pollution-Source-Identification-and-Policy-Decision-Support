import requests


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