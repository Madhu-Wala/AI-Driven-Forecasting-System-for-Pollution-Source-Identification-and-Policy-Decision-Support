import os
import requests
from dotenv import load_dotenv

load_dotenv()

WAQI_TOKEN = os.getenv("WAQI_TOKEN")

SEARCH_URL = "https://api.waqi.info/search/"
FEED_URL = "https://api.waqi.info/feed/@{uid}/"

# Mumbai bounding box
MIN_LAT = 18.89
MAX_LAT = 19.27
MIN_LON = 72.75
MAX_LON = 73.00


def get_mumbai_stations():
    params = {
        "token": WAQI_TOKEN,
        "keyword": "mumbai"
    }

    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"WAQI search failed: {data}")

    stations = data.get("data", [])

    # Keep only stations within Mumbai
    mumbai_stations = []

    for station in stations:
        geo = station.get("station", {}).get("geo")

        if not geo or len(geo) != 2:
            continue

        lat, lon = geo

        if (
            MIN_LAT <= lat <= MAX_LAT
            and MIN_LON <= lon <= MAX_LON
        ):
            mumbai_stations.append(station)

    return mumbai_stations


def get_station_details(uid):
    url = FEED_URL.format(uid=uid)

    params = {
        "token": WAQI_TOKEN
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(
            f"WAQI station fetch failed for UID {uid}: {data}"
        )

    return data.get("data", {})


def get_all_mumbai_station_details():
    stations = get_mumbai_stations()

    results = []

    for station in stations:
        uid = station.get("uid")

        if not uid:
            continue

        try:
            details = get_station_details(uid)

            results.append(details)

        except Exception as error:
            print(
                f"Failed to fetch WAQI station {uid}: {error}"
            )

    return results