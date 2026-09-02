from app.services.providers.google_air_quality_provider import (
    get_current_air_quality
)

from app.services.parsers.google_air_quality_parser import (
    parse_current_air_quality
)


async def get_current(latitude: float, longitude: float):
    """
    Fetch current air-quality data for a location.

    Google provides:
    - India CPCB/NAQI AQI
    - Universal AQI
    - Pollutant concentrations
    - Dominant pollutant
    """

    raw_data = await get_current_air_quality(
        latitude=latitude,
        longitude=longitude
    )

    return parse_current_air_quality(raw_data)