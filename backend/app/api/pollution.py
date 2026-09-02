from fastapi import APIRouter, HTTPException

from app.services.pollution_service import (
    get_current_mumbai_pollution
)


router = APIRouter(
    prefix="/api/pollution",
    tags=["Pollution"]
)


@router.get("/current")
async def current_pollution():
    """
    Return current Google-based AQI information
    for Mumbai monitoring station locations.
    """

    try:

        data = await get_current_mumbai_pollution()

        return {
            "source": "Google Air Quality API",
            "count": len(data),
            "stations": data
        }

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=str(e)
        )