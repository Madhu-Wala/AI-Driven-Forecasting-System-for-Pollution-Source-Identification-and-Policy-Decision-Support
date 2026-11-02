import logging

from fastapi import APIRouter, HTTPException

from app.services.source_identification_service import (
    get_all_source_identification_results,
    get_source_identification_by_station
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/source-identification",
    tags=["Source Identification"]
)


@router.get("/")
def get_all_source_results():

    try:
        results = get_all_source_identification_results()

        return {
            "source": "Neon PostgreSQL",
            "method": "Pollutant-Anomaly-Based Heuristic Source Identification",
            "count": len(results),
            "stations": results
        }

    except Exception as e:

        logger.exception("Source identification API failed")

        raise HTTPException(
            status_code=503,
            detail=str(e)
        )


@router.get("/{station_id}")
def get_station_source_result(station_id: str):

    try:
        result = get_source_identification_by_station(
            station_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No source identification data found for {station_id}"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            "Source identification failed for %s",
            station_id
        )

        raise HTTPException(
            status_code=503,
            detail=str(e)
        )