
from fastapi import APIRouter, HTTPException, Query

from app.services.hotspot_service import (
    get_hotspots,
    get_hotspot_by_station
)


router = APIRouter(
    prefix="/api/hotspots",
    tags=["Hotspot Identification"]
)


@router.get("/")
def fetch_hotspots(
    limit: int = Query(default=10, ge=1, le=20)
):
    """
    Return the highest-AQI stations as ranked hotspots.
    """

    try:
        hotspots = get_hotspots(limit=limit)

        return {
            "total_hotspots": len(hotspots),
            "ranking_criteria": "AQI descending",
            "hotspots": hotspots
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to identify hotspots: {str(e)}"
        )


@router.get("/{station_id}")
def fetch_hotspot(station_id: str):
    """
    Return hotspot information for a particular station.
    """

    try:
        hotspot = get_hotspot_by_station(station_id)

        if hotspot is None:
            raise HTTPException(
                status_code=404,
                detail="Station not found."
            )

        return hotspot

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to fetch hotspot: {str(e)}"
        )
