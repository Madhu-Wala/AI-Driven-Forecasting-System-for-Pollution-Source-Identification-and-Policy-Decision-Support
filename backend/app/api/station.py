from fastapi import APIRouter
from app.services.station_service import station_service

router=APIRouter(
    prefix="/station",
    tags=["Station Lookup"]
)

@router.get("/")
def nearest_station(lat:float, lon:float):
    return station_service.get_nearest_station(lat, lon)