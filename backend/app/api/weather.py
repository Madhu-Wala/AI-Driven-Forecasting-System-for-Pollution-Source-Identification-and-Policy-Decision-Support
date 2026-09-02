from fastapi import APIRouter, HTTPException, Query

from app.services.weather_service import get_weather_for_location


router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/forecast")
def weather_forecast(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    forecast_days: int = Query(
        2,
        ge=1,
        le=10,
        description="Number of forecast days"
    )
):
    """
    Get weather forecast for a latitude/longitude.
    """

    try:
        weather_df = get_weather_for_location(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days
        )

        # Convert DataFrame to JSON-compatible records
        records = weather_df.to_dict(
            orient="records"
        )

        # Convert Timestamp to string
        for record in records:
            if hasattr(record["date"], "strftime"):
                record["date"] = record["date"].strftime(
                    "%Y-%m-%d"
                )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": len(records),
            "source": "Open-Meteo",
            "forecast": records
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch weather data: {str(e)}"
        )