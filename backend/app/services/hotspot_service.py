
from app.services.source_identification_service import (
    get_all_source_identification_results
)


def get_hotspots(limit: int = 10):
    """
    Identify and rank pollution hotspots using the
    existing source-identification results.

    AQI is the primary ranking factor.
    Source-identification details are preserved.
    """

    station_results = get_all_source_identification_results()

    if not station_results:
        return []

    # Sort stations by AQI in descending order.
    ranked_stations = sorted(
        station_results,
        key=lambda station: float(station.get("aqi") or 0),
        reverse=True
    )

    hotspots = []

    for rank, station in enumerate(ranked_stations[:limit], start=1):

        hotspot = station.copy()

        hotspot["hotspot_rank"] = rank

        hotspots.append(hotspot)

    return hotspots


def get_hotspot_by_station(station_id: str):
    """
    Return hotspot details for one station.
    """

    hotspots = get_hotspots(limit=20)

    for hotspot in hotspots:
        if hotspot.get("station_id") == station_id:
            return hotspot

    return None
