from fastapi import APIRouter, HTTPException

from app.services.analytics_service import (
    get_station_historical_analytics
)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/history/{station_id}")
def get_analytics_history(station_id: str):

    try:
        result = get_station_historical_analytics(station_id)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch historical analytics: {str(e)}"
        )
