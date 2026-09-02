from fastapi import APIRouter, HTTPException, Query

from app.services.air_quality_service import get_current


router = APIRouter(
    prefix="/api/air-quality",
    tags=["Air Quality"]
)


@router.get("/current")
async def current_air_quality(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    try:
        return await get_current(
            latitude=lat,
            longitude=lon
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch current air quality: {str(e)}"
        )