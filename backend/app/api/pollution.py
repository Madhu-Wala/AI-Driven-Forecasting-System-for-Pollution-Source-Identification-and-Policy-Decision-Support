from fastapi import APIRouter, HTTPException
from app.services.pollution_service import (get_current_mumbai_pollution)

router=APIRouter(
    prefix="/api/pollution",
    tags=["Pollution"]
)

@router.get("/current")
def current_pollution():
    """
    Return current pollution information
    for Mumbai monitoring stations.
    """
    try:
        data=get_current_mumbai_pollution()
        return{
            # "city":"Mumbai",
            # "stations":data
            "source": "WAQI",
            "count": len(data),
            "stations": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )