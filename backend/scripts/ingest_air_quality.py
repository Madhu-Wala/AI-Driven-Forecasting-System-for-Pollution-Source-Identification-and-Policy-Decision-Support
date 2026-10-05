import os
import time
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

from datetime import datetime
from zoneinfo import ZoneInfo
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURATION
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_AIR_QUALITY_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

HISTORY_URL = "https://airquality.googleapis.com/v1/history:lookup"

IST = ZoneInfo("Asia/Kolkata")

def validate_environment():
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_AIR_QUALITY_API_KEY is not configured."
        )

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )


def get_database_connection():
    return psycopg2.connect(DATABASE_URL)


# ============================================================
# STATIONS
# ============================================================

STATIONS = [
    {
        "station_encoded": 0,
        "display_name": "Bandra Kurla Complex",
        "latitude": 19.0606629,
        "longitude": 72.8546797
    },
    {
        "station_encoded": 1,
        "display_name": "Borivali East MPCB",
        "latitude": 19.2187,
        "longitude": 72.8655
    },
    {
        "station_encoded": 2,
        "display_name": "Borivali East",
        "latitude": 19.2187187,
        "longitude": 72.8654856
    },
    {
        "station_encoded": 3,
        "display_name": "Chakala-Andheri East",
        "latitude": 19.1136556,
        "longitude": 72.8585799
    },
    {
        "station_encoded": 4,
        "display_name": "Chhatrapati Shivaji Intl. Airport (T2)",
        "latitude": 19.0896,
        "longitude": 72.8656
    },
    {
        "station_encoded": 5,
        "display_name": "Colaba",
        "latitude": 18.915091,
        "longitude": 72.8259691
    },
    {
        "station_encoded": 6,
        "display_name": "Deonar",
        "latitude": 19.0475502,
        "longitude": 72.9051895
    },
    {
        "station_encoded": 7,
        "display_name": "Kandivali East",
        "latitude": 19.1990695,
        "longitude": 72.8482288
    },
    {
        "station_encoded": 8,
        "display_name": "Khindipada-Bhandup West",
        "latitude": 19.1605651,
        "longitude": 72.9289692
    },
    {
        "station_encoded": 9,
        "display_name": "Kurla",
        "latitude": 19.0652797,
        "longitude": 72.8793805
    },
    {
        "station_encoded": 10,
        "display_name": "Mahape, Navi Mumbai",
        "latitude": 19.1093012,
        "longitude": 73.0235724
    },
    {
        "station_encoded": 11,
        "display_name": "Malad West",
        "latitude": 19.1852851,
        "longitude": 72.8358611
    },
    {
        "station_encoded": 12,
        "display_name": "Mazgaon",
        "latitude": 18.9697337,
        "longitude": 72.8406201
    },
    {
        "station_encoded": 13,
        "display_name": "Mulund West",
        "latitude": 19.1719717,
        "longitude": 72.9511956
    },
    {
        "station_encoded": 14,
        "display_name": "Navy Nagar-Colaba",
        "latitude": 18.9074266,
        "longitude": 72.8083029
    },
    {
        "station_encoded": 15,
        "display_name": "Nerul, Navi Mumbai",
        "latitude": 19.0335938,
        "longitude": 73.018164
    },
    {
        "station_encoded": 16,
        "display_name": "Powai",
        "latitude": 19.1187195,
        "longitude": 72.9073476
    },
    {
        "station_encoded": 17,
        "display_name": "Siddharth Nagar Worli",
        "latitude": 19.017,
        "longitude": 72.815
    },
    {
        "station_encoded": 18,
        "display_name": "Sion",
        "latitude": 19.0465213,
        "longitude": 72.8632834
    },
    {
        "station_encoded": 19,
        "display_name": "Worli",
        "latitude": 18.9988405,
        "longitude": 72.8170327
    }
]

def convert_to_ist(timestamp):
    dt = datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    )

    return dt.astimezone(IST)

MOLECULAR_WEIGHTS = {
    "no2": 46.0055,
    "so2": 64.066,
    "co": 28.01,
    "o3": 47.9982
}


def convert_to_ug_m3(code, value, unit):

    if value is None:
        return None

    value = float(value)

    if unit == "MICROGRAMS_PER_CUBIC_METER":
        return value

    if unit == "PARTS_PER_BILLION":

        molecular_weight = MOLECULAR_WEIGHTS.get(code)

        if molecular_weight:
            return value * molecular_weight / 24.45

    if unit == "PARTS_PER_MILLION":

        molecular_weight = MOLECULAR_WEIGHTS.get(code)

        if molecular_weight:
            return value * 1000 * molecular_weight / 24.45

    return value

def extract_india_aqi(indexes):

    for index in indexes or []:

        if index.get("code") == "ind_cpcb":

            return {
                "aqi": index.get("aqi"),
                "category": index.get("category"),
                "dominant_pollutant": index.get(
                    "dominantPollutant"
                )
            }

    return {
        "aqi": None,
        "category": None,
        "dominant_pollutant": None
    }

def extract_pollutants(pollutants):

    result = {
        "pm25": None,
        "pm10": None,
        "no2": None,
        "so2": None,
        "co": None,
        "o3": None
    }

    for pollutant in pollutants or []:

        code = pollutant.get("code")

        if code not in result:
            continue

        concentration = pollutant.get(
            "concentration",
            {}
        )

        value = concentration.get("value")
        unit = concentration.get("units")

        if value is not None:
            value = convert_to_ug_m3(
                code,
                value,
                unit
            )

        result[code] = value

    return result

def fetch_station_history(
    latitude,
    longitude,
    hours=3
):

    payload = {
        "location": {
            "latitude": float(latitude),
            "longitude": float(longitude)
        },
        "hours": hours,
        "pageSize": 168,
        "universalAqi": True,
        "extraComputations": [
            "LOCAL_AQI",
            "POLLUTANT_CONCENTRATION"
        ],
        "languageCode": "en"
    }

    response = requests.post(
        HISTORY_URL,
        params={"key": GOOGLE_API_KEY},
        json=payload,
        timeout=30
    )

    if response.status_code != 200:

        print(
            f"Google API error "
            f"{response.status_code}:"
        )

        print(response.text[:1000])

        response.raise_for_status()

    return response.json().get(
        "hoursInfo",
        []
    )

def normalize_records(
    station,
    hours_info
):

    records = []

    station_id = (
        f"station_{station['station_encoded']}"
    )

    for hour in hours_info:

        timestamp = hour.get("dateTime")

        if not timestamp:
            continue

        timestamp = convert_to_ist(
            timestamp
        )

        aqi_info = extract_india_aqi(
            hour.get("indexes", [])
        )

        pollutant_info = extract_pollutants(
            hour.get("pollutants", [])
        )

        records.append({

            "station_id": station_id,

            "station_name":
                station["display_name"],

            "latitude":
                station["latitude"],

            "longitude":
                station["longitude"],

            "timestamp":
                timestamp,

            "aqi":
                aqi_info["aqi"],

            "aqi_category":
                aqi_info["category"],

            "pm25":
                pollutant_info["pm25"],

            "pm10":
                pollutant_info["pm10"],

            "no2":
                pollutant_info["no2"],

            "so2":
                pollutant_info["so2"],

            "co":
                pollutant_info["co"],

            "o3":
                pollutant_info["o3"],

            "source":
                "Google Air Quality API"
        })

    return records

INSERT_SQL = """
INSERT INTO "air_quality-data" (
    station_id,
    station_name,
    latitude,
    longitude,
    timestamp,
    aqi,
    aqi_category,
    pm25,
    pm10,
    no2,
    so2,
    co,
    o3,
    source
)
VALUES %s

ON CONFLICT (
    station_id,
    timestamp,
    source
)
DO NOTHING;
"""

def insert_records(conn, records):

    if not records:
        return 0

    values = [

        (
            r["station_id"],
            r["station_name"],
            r["latitude"],
            r["longitude"],
            r["timestamp"],
            r["aqi"],
            r["aqi_category"],
            r["pm25"],
            r["pm10"],
            r["no2"],
            r["so2"],
            r["co"],
            r["o3"],
            r["source"]
        )

        for r in records
    ]

    with conn.cursor() as cursor:

        execute_values(
            cursor,
            INSERT_SQL,
            values,
            page_size=100
        )

    conn.commit()

    return len(values)

def main():

    validate_environment()

    print("=" * 70)
    print("Mumbai Air Quality Hourly Ingestion")
    print("=" * 70)

    conn = get_database_connection()

    total_received = 0
    total_inserted = 0

    try:

        for index, station in enumerate(STATIONS, start=1):

            print()
            print(
                f"[{index}/20] "
                f"{station['display_name']}"
            )

            try:

                history = fetch_station_history(
                    latitude=station["latitude"],
                    longitude=station["longitude"],
                    hours=3
                )

                records = normalize_records(
                    station,
                    history
                )

                inserted = insert_records(
                    conn,
                    records
                )

                total_received += len(records)
                total_inserted += inserted

                print(
                    f"  Received: {len(records)}"
                )

                print(
                    f"  Inserted:  {inserted}"
                )

            except Exception as e:

                print(
                    f"  ❌ Failed: {e}"
                )

            time.sleep(2)

    finally:

        conn.close()

    print()
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"Total records received: {total_received}"
    )

    print(
        f"Total records inserted: {total_inserted}"
    )


if __name__ == "__main__":
    main()