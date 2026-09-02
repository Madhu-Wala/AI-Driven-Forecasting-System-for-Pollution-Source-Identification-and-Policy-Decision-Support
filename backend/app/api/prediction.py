from fastapi import APIRouter, HTTPException, Query

from app.services.weather_service import (
    get_weather_for_location
)

from app.services.prediction_service import (
    predict_future_aqi
)

from app.services.air_quality_service import (
    get_current
)



router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)
# =========================================================
# FORECAST ENDPOINT
# =========================================================

@router.get("/forecast")
async def prediction_forecast(

    latitude: float = Query(
        ...,
        description="User latitude"
    ),

    longitude: float = Query(
        ...,
        description="User longitude"
    ),

    forecast_days: int = Query(
        3,
        ge=1,
        le=7,
        description="Number of days to predict"
    )
):

    try:

        # =================================================
        # 1. CURRENT AIR QUALITY FROM GOOGLE
        # =================================================

        current_air_quality = await get_current(
            latitude=latitude,
            longitude=longitude
        )

        current_aqi = current_air_quality.get("aqi")

        if current_aqi is None:
            raise ValueError(
                "Current AQI is not available."
            )

        # Get pollutant concentrations
        pollutants = (
            current_air_quality.get("pollutants", {})
        )

        # =================================================
        # 2. WEATHER FORECAST
        # =================================================

        weather_df = get_weather_for_location(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days
        )

        weather_records = weather_df.to_dict(
            orient="records"
        )

        for record in weather_records:

            if hasattr(
                record["date"],
                "strftime"
            ):
                record["date"] = (
                    record["date"]
                    .strftime("%Y-%m-%d")
                )

        # =================================================
        # 3. AQI PREDICTION
        # =================================================

        result = predict_future_aqi(

            weather_forecast=weather_records,

            latitude=latitude,

            longitude=longitude,

            current_aqi=current_aqi
        )

        # =================================================
        # 4. RESPONSE
        # =================================================

        return {

            "source":
                "LightGBM + Open-Meteo + Google Air Quality API",

            "latitude":
                latitude,

            "longitude":
                longitude,

            "current_AQI":
                round(float(current_aqi), 2),

            "aqi_category":
                current_air_quality.get("category"),

            "dominant_pollutant":
                current_air_quality.get(
                    "dominant_pollutant"
                ),

            "pollutants":
                pollutants,

            **result

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AQI prediction failed: {str(e)}"
        )