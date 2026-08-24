import os
import requests
from dotenv import load_dotenv

load_dotenv()

CPCB_API_KEY = os.getenv("DATA_GOV_API_KEY")
CPCB_RESOURCE_ID = os.getenv("RESOURCE_ID")
CPCB_BASE_URL = f"https://api.data.gov.in/resource/{CPCB_RESOURCE_ID}"

def get_mumbai_pollution():
    """
    Fetch real-time pollution records for Mumbai
    from the CPCB/data.gov.in API.

    Returns:
        list: Raw CPCB records.
    """

    if not CPCB_API_KEY or not CPCB_RESOURCE_ID:
        raise ValueError("Missing CPCB configuration in environment variables.")

    params={
        "api-key": CPCB_API_KEY,
        "format": "json",
        "filters[city]": "Mumbai",
        "limit": 500
    }

    response=requests.get(CPCB_BASE_URL,params=params,timeout=10)
    response.raise_for_status()

    data=response.json()
    return data.get("records", [])

def get_station_pollution(station_name: str):
    """
    Get CPCB pollution records for a particular station.

    Args:
        station_name: Exact CPCB station name.

    Returns:
        dict: Grouped station pollution information,
        or None if station is not found.
    """

    records=get_mumbai_pollution()
    station_records=[
        record
        for record in records
        if record.get("station") == station_name
    ]

    if not station_records:
        return None

    first_record=station_records[0]
    pollutants={}

    for record in station_records:
        pollutant_id=record.get("pollutant_id")
        avg_value=record.get("avg_value")
        if pollutant_id:
            pollutants[pollutant_id.lower()]=avg_value

    return {
        "station": first_record.get("station"),
        "latitude": first_record.get("latitude"),
        "longitude": first_record.get("longitude"),
        "last_update": first_record.get("last_update"),
        "pollutants": pollutants
    }