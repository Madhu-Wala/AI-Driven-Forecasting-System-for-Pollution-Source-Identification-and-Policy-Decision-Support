import os
import logging

import pandas as pd
from dotenv import load_dotenv

from app.utils.station_mapping import find_nearest_historical_station

from app.services.providers.waqi_provider import (
    get_all_mumbai_station_details
)

from app.services.providers.cpcb_provider import (
    get_mumbai_pollution
)


# ============================================================
# Configuration
# ============================================================

load_dotenv()

HISTORICAL_DATASET = os.getenv("HISTORICAL_DATASET_PATH")


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# Constants
# ============================================================

POLLUTANTS = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3"
]

POLLUTANT_MAPPING = {
    "pm25": "pm25",
    "pm10": "pm10",
    "no2": "no2",
    "so2": "so2",
    "co": "co",
    "o3": "o3",
    "ozone": "o3"
}

REQUIRED_HISTORICAL_COLUMNS = {
    "date",
    "station",
    "latitude",
    "longitude",
    "station_encoded",
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3"
}


# ============================================================
# Historical Dataset
# ============================================================

def load_historical_data():
    """
    Load and validate the historical pollution dataset.

    The dataset is used for:
    1. Mapping live stations to historical stations.
    2. Imputing missing pollutant values.
    3. Providing station_encoded values for ML prediction.
    """

    if not HISTORICAL_DATASET:
        raise RuntimeError(
            "HISTORICAL_DATASET_PATH is not configured in .env"
        )

    if not os.path.isfile(HISTORICAL_DATASET):
        raise FileNotFoundError(
            f"Historical dataset not found: {HISTORICAL_DATASET}"
        )

    df = pd.read_csv(HISTORICAL_DATASET)

    missing_columns = (
        REQUIRED_HISTORICAL_COLUMNS - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Historical dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["month"] = df["date"].dt.month

    # Remove rows without valid station coordinates.
    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["station", "latitude", "longitude"]
    )

    if df.empty:
        raise ValueError(
            "Historical dataset contains no usable station records."
        )

    logger.info(
        "Historical dataset loaded successfully: %d rows",
        len(df)
    )

    return df


# ============================================================
# Value Validation
# ============================================================

def is_invalid_value(value, pollutant):
    """
    Validate live pollutant values.

    Rejects:
    - None
    - empty strings
    - "-"
    - N/A/null
    - known sentinel values such as 999
    - physically implausible values
    """

    if value is None:
        return True

    if isinstance(value, str):
        if value.strip().lower() in ["", "-", "n/a", "na", "null"]:
            return True

    try:
        value = float(value)
    except (ValueError, TypeError):
        return True

    if value < 0:
        return True

    # WAQI commonly uses 999 as an unavailable/sentinel value
    if value == 999:
        return True

    # PM2.5 / PM10 values this high are treated as invalid
    # for our application and replaced using historical fallback.
    if pollutant == "pm25" and value > 500:
        return True

    if pollutant == "pm10" and value > 600:
        return True

    return False

# ============================================================
# Historical Median
# ============================================================

def get_historical_median(
    historical_df,
    station_name,
    pollutant,
    month
):
    """
    Get a historical median value using this hierarchy:

    Level 1:
        Same historical station + same month

    Level 2:
        Mumbai-wide + same month

    Returns:
        float or None
    """

    column_map = {
        "pm25": "pm25",
        "pm10": "pm10",
        "no2": "no2",
        "so2": "so2",
        "co": "co",
        "o3": "o3"
    }

    column = column_map.get(pollutant)

    if column is None:
        raise ValueError(
            f"Unsupported pollutant: {pollutant}"
        )

    # --------------------------------------------------------
    # Level 1: Same station + same month
    # --------------------------------------------------------

    station_data = historical_df[
        (historical_df["station"] == station_name)
        & (historical_df["month"] == month)
    ][column]

    station_data = pd.to_numeric(
        station_data,
        errors="coerce"
    ).dropna()

    # Remove known invalid sentinel values from historical data.
    station_data = station_data[
        station_data != 999
    ]

    if not station_data.empty:
        return float(station_data.median())

    # --------------------------------------------------------
    # Level 2: Mumbai-wide + same month
    # --------------------------------------------------------

    monthly_data = historical_df[
        historical_df["month"] == month
    ][column]

    monthly_data = pd.to_numeric(
        monthly_data,
        errors="coerce"
    ).dropna()

    monthly_data = monthly_data[
        monthly_data != 999
    ]

    if not monthly_data.empty:
        return float(monthly_data.median())

    # No historical value available.
    return None


# ============================================================
# Station Data Cleaning
# ============================================================

def clean_station_data(
    station,
    historical_df
):
    """
    Validate and clean one live station.

    Steps:
    1. Validate station coordinates.
    2. Find exact/nearest historical station.
    3. Validate live pollutant values.
    4. Impute missing pollutants using historical medians.
    5. Return station metadata required by the ML pipeline.
    """

    station_name = station.get("station")

    if not station_name:
        raise ValueError(
            "Station name is missing."
        )

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    latitude = station.get("latitude")
    longitude = station.get("longitude")

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid coordinates for station: {station_name}"
        )

    if not (-90 <= latitude <= 90):
        raise ValueError(
            f"Invalid latitude for station {station_name}: "
            f"{latitude}"
        )

    if not (-180 <= longitude <= 180):
        raise ValueError(
            f"Invalid longitude for station {station_name}: "
            f"{longitude}"
        )

    # --------------------------------------------------------
    # Find exact / nearest historical station
    # --------------------------------------------------------

    station_mapping = find_nearest_historical_station(
        latitude,
        longitude,historical_df
    )

    if not station_mapping:
        raise ValueError(
            f"No historical station mapping found for "
            f"{station_name}"
        )

    historical_station_name = (
        station_mapping.get("historical_station")
    )

    station_encoded = (
        station_mapping.get("station_encoded")
    )

    distance_km = (
        station_mapping.get("distance_km")
    )

    if not historical_station_name:
        raise ValueError(
            f"Historical station mapping missing for "
            f"{station_name}"
        )

    if station_encoded is None:
        raise ValueError(
            f"station_encoded missing for "
            f"{historical_station_name}"
        )

    # --------------------------------------------------------
    # Determine month
    # --------------------------------------------------------

    timestamp = pd.to_datetime(
        station.get("timestamp"),
        errors="coerce"
    )

    if pd.isna(timestamp):
        month = pd.Timestamp.now().month
    else:
        month = timestamp.month

    # --------------------------------------------------------
    # Clean / impute pollutants
    # --------------------------------------------------------

    cleaned_pollutants = {}
    imputation_flags = {}

    for pollutant in POLLUTANTS:

        live_value = (
            station.get("pollutants", {})
            .get(pollutant)
        )

        # ----------------------------------------------------
        # Valid live value
        # ----------------------------------------------------

        if not is_invalid_value(live_value,pollutant):

            cleaned_pollutants[pollutant] = float(
                live_value
            )

            imputation_flags[pollutant] = False

            continue

        # ----------------------------------------------------
        # Missing/invalid live value
        # → historical fallback
        # ----------------------------------------------------

        fallback = get_historical_median(
            historical_df=historical_df,
            station_name=historical_station_name,
            pollutant=pollutant,
            month=month
        )

        if fallback is None:

            raise ValueError(
                f"No fallback value available for "
                f"{pollutant} at station {station_name}"
            )

        cleaned_pollutants[pollutant] = fallback
        imputation_flags[pollutant] = True

    # --------------------------------------------------------
    # Clean AQI
    # --------------------------------------------------------

    aqi = station.get("aqi")

    if is_invalid_value(aqi):
        cleaned_aqi = None
    else:
        cleaned_aqi = float(aqi)

    # --------------------------------------------------------
    # Return normalized station
    # --------------------------------------------------------

    return {
        "station": station_name,

        "latitude": latitude,
        "longitude": longitude,

        "timestamp": station.get("timestamp"),

        "aqi": cleaned_aqi,

        "pollutants": cleaned_pollutants,

        "imputed": imputation_flags,

        "source": station.get("source"),

        # Historical mapping information
        "historical_station": historical_station_name,

        "station_encoded": station_encoded,

        "historical_latitude": station_mapping.get(
            "historical_latitude"
        ),

        "historical_longitude": station_mapping.get(
            "historical_longitude"
        ),

        "mapping_distance_km": distance_km,

        "is_fallback_station": (
            station_name != historical_station_name
        )
    }


# ============================================================
# WAQI Normalization
# ============================================================

def normalize_waqi_station(data):
    """
    Convert a WAQI station response into the application's
    common station format.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid WAQI station response."
        )

    city = data.get("city") or {}
    iaqi = data.get("iaqi") or {}
    time_data = data.get("time") or {}

    geo = city.get("geo")

    if not isinstance(geo, (list, tuple)) or len(geo) < 2:
        raise ValueError(
            "WAQI station does not contain valid coordinates."
        )

    return {
        "station": city.get("name"),

        "latitude": geo[0],
        "longitude": geo[1],

        "timestamp": time_data.get("s"),

        "aqi": data.get("aqi"),

        "pollutants": {
            "pm25": (
                iaqi.get("pm25", {}).get("v")
                if isinstance(iaqi.get("pm25"), dict)
                else None
            ),

            "pm10": (
                iaqi.get("pm10", {}).get("v")
                if isinstance(iaqi.get("pm10"), dict)
                else None
            ),

            "no2": (
                iaqi.get("no2", {}).get("v")
                if isinstance(iaqi.get("no2"), dict)
                else None
            ),

            "so2": (
                iaqi.get("so2", {}).get("v")
                if isinstance(iaqi.get("so2"), dict)
                else None
            ),

            "co": (
                iaqi.get("co", {}).get("v")
                if isinstance(iaqi.get("co"), dict)
                else None
            ),

            "o3": (
                iaqi.get("o3", {}).get("v")
                if isinstance(iaqi.get("o3"), dict)
                else None
            )
        },

        "source": "WAQI"
    }


# ============================================================
# CPCB Normalization
# ============================================================

def normalize_cpcb_records(records):
    """
    Convert CPCB/data.gov.in pollutant-row format into
    the application's common station format.

    CPCB returns multiple records for one station,
    generally one record per pollutant.
    """

    if not isinstance(records, list):
        raise ValueError(
            "Invalid CPCB response format."
        )

    stations = {}

    for record in records:

        if not isinstance(record, dict):
            continue

        station_name = record.get("station")

        if not station_name:
            continue

        # ----------------------------------------------------
        # Create station entry
        # ----------------------------------------------------

        if station_name not in stations:

            stations[station_name] = {
                "station": station_name,

                "latitude": record.get("latitude"),

                "longitude": record.get("longitude"),

                "timestamp": record.get(
                    "last_update"
                ),

                "aqi": None,

                "pollutants": {},

                "source": "CPCB"
            }

        # ----------------------------------------------------
        # Process pollutant
        # ----------------------------------------------------

        pollutant_id = record.get(
            "pollutant_id"
        )

        if not pollutant_id:
            continue

        pollutant_key = POLLUTANT_MAPPING.get(
            str(pollutant_id).lower()
        )

        if pollutant_key is None:
            continue

        value = record.get("avg_value")

        if not is_invalid_value(value):

            stations[station_name]["pollutants"][
                pollutant_key
            ] = float(value)

    return list(stations.values())


# ============================================================
# Main Pollution Service
# ============================================================

def get_current_mumbai_pollution():
    """
    Fetch current Mumbai pollution data.

    Provider priority:

        1. WAQI
        2. CPCB

    Both providers go through the same normalization,
    station mapping and historical fallback pipeline.

    Returns:
        list of cleaned station records.
    """

    # --------------------------------------------------------
    # Load historical dataset
    # --------------------------------------------------------

    historical_df = load_historical_data()

    # ========================================================
    # PRIMARY PROVIDER: WAQI
    # ========================================================

    try:

        logger.info(
            "Fetching Mumbai pollution data from WAQI..."
        )

        waqi_data = get_all_mumbai_station_details()

        if not waqi_data:
            raise RuntimeError(
                "WAQI returned no station data."
            )

        results = []

        for station_data in waqi_data:

            try:

                normalized = normalize_waqi_station(
                    station_data
                )

                cleaned = clean_station_data(
                    normalized,
                    historical_df
                )

                results.append(cleaned)

            except Exception as station_error:

                station_name = (
                    station_data
                    .get("city", {})
                    .get("name", "Unknown station")
                    if isinstance(station_data, dict)
                    else "Unknown station"
                )

                logger.warning(
                    "Skipping WAQI station '%s': %s",
                    station_name,
                    station_error
                )

        if results:

            logger.info(
                "WAQI successfully provided %d usable stations.",
                len(results)
            )

            return results

        raise RuntimeError(
            "WAQI returned data, but no usable stations "
            "remained after validation."
        )

    except Exception as waqi_error:

        logger.warning(
            "WAQI provider failed: %s",
            waqi_error
        )

    # ========================================================
    # FALLBACK PROVIDER: CPCB
    # ========================================================

    try:

        logger.info(
            "Attempting CPCB pollution provider..."
        )

        cpcb_records = get_mumbai_pollution()

        if not cpcb_records:
            raise RuntimeError(
                "CPCB returned no pollution records."
            )

        cpcb_stations = normalize_cpcb_records(
            cpcb_records
        )

        results = []

        for station in cpcb_stations:

            try:

                cleaned = clean_station_data(
                    station,
                    historical_df
                )

                results.append(cleaned)

            except Exception as station_error:

                logger.warning(
                    "Skipping CPCB station '%s': %s",
                    station.get("station", "Unknown station"),
                    station_error
                )

        if results:

            logger.info(
                "CPCB successfully provided %d usable stations.",
                len(results)
            )

            return results

        raise RuntimeError(
            "CPCB returned data, but no usable stations "
            "remained after validation."
        )

    except Exception as cpcb_error:

        logger.error(
            "CPCB provider failed: %s",
            cpcb_error
        )

        raise RuntimeError(
            "Both WAQI and CPCB providers failed to "
            "provide usable pollution data."
        ) from cpcb_error