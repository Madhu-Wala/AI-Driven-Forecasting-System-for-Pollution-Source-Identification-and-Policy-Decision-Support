from fastapi import APIRouter, HTTPException, Query

from app.services.air_quality_service import (
    get_current
)

from app.services.shap_service import (
    explain_current_pollution
)


router = APIRouter(
    prefix="/shap",
    tags=["SHAP"]
)


@router.get("/current")
async def current_pollutant_contribution(

    latitude: float = Query(
        ...,
        description="User latitude"
    ),

    longitude: float = Query(
        ...,
        description="User longitude"
    )
):

    try:

        current_air_quality = await get_current(
            latitude=latitude,
            longitude=longitude
        )

        current_aqi = current_air_quality.get(
            "aqi"
        )

        if current_aqi is None:
            raise ValueError(
                "Current AQI is not available."
            )

        pollutants = current_air_quality.get(
            "pollutants",
            {}
        )

        shap_result = explain_current_pollution(
            pollutants
        )

        return {
            "latitude": latitude,
            "longitude": longitude,

            "current_AQI": round(
                float(current_aqi),
                2
            ),

            "aqi_category":
                current_air_quality.get(
                    "category"
                ),

            "dominant_pollutant":
                current_air_quality.get(
                    "dominant_pollutant"
                ),

            "pollutants":
                pollutants,

            "shap_analysis":
                shap_result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"SHAP analysis failed: {str(e)}"
        )