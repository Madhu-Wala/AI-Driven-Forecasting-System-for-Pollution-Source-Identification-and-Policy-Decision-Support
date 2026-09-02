import pandas as pd

from app.services.providers.weather_provider import (
    get_weather_forecast
)


def get_weather_for_location(
    latitude,
    longitude,
    forecast_days=2
):
    """
    Get weather forecast and prepare features
    required by the prediction model.
    """

    weather_records = get_weather_forecast(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days
    )

    df = pd.DataFrame(weather_records)

    if df.empty:
        raise RuntimeError(
            "No weather data returned."
        )

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Remove invalid dates
    df = df.dropna(
        subset=["date"]
    )

    # Features required by prediction model
    df["month"] = df["date"].dt.month
    df["dayofyear"] = df["date"].dt.dayofyear

    # Location
    df["latitude"] = float(latitude)
    df["longitude"] = float(longitude)

    return df