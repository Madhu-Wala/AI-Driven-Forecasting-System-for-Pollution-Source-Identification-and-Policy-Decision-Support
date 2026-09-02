import os
import logging

import pandas as pd
from dotenv import load_dotenv

from app.utils.station_mapping import find_nearest_historical_station

from app.services.providers.google_air_quality_provider import (
    get_current_air_quality
)

from app.utils.cache import get_cache, set_cache

# ============================================================
# Configuration
# ============================================================

load_dotenv()

HISTORICAL_DATASET = os.getenv(
    "HISTORICAL_DATASET_PATH"
)


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

    if not HISTORICAL_DATASET:
        raise RuntimeError(
            "HISTORICAL_DATASET_PATH is not configured in .env"
        )

    if not os.path.isfile(HISTORICAL_DATASET):
        raise FileNotFoundError(
            f"Historical dataset not found: "
            f"{HISTORICAL_DATASET}"
        )

    df = pd.read_csv(
        HISTORICAL_DATASET
    )

    missing_columns = (
        REQUIRED_HISTORICAL_COLUMNS
        - set(df.columns)
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

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "station",
            "latitude",
            "longitude"
        ]
    )

    if df.empty:
        raise ValueError(
            "Historical dataset contains no usable "
            "station records."
        )

    logger.info(
        "Historical dataset loaded successfully: %d rows",
        len(df)
    )

    return df

# ============================================================
# AQI Color
# ============================================================

def get_aqi_color(aqi):

    if aqi is None:
        return None

    aqi = float(aqi)

    if aqi <= 50:
        return "#00E400"

    elif aqi <= 100:
        return "#FFFF00"

    elif aqi <= 200:
        return "#FF7E00"

    elif aqi <= 300:
        return "#FF0000"

    elif aqi <= 400:
        return "#8F3F97"

    else:
        return "#7E0023"

# ============================================================
# Value Validation
# ============================================================

def is_invalid_value(
    value,
    pollutant=None
):
    """
    Validate pollutant/AQI values.

    Invalid values:
    - None
    - empty strings
    - '-'
    - N/A / NA / null
    - negative values
    - 999 sentinel
    - extremely high PM2.5
    - extremely high PM10
    """

    if value is None:
        return True

    if isinstance(value, str):

        cleaned = value.strip().lower()

        if cleaned in [
            "",
            "-",
            "n/a",
            "na",
            "null"
        ]:
            return True

    try:
        value = float(value)

    except (
        ValueError,
        TypeError
    ):
        return True

    if value < 0:
        return True

    # Common unavailable/sentinel value
    if value == 999:
        return True

    # Extremely high PM2.5
    if (
        pollutant == "pm25"
        and value > 500
    ):
        return True

    # Extremely high PM10
    if (
        pollutant == "pm10"
        and value > 600
    ):
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

    column_map = {
        "pm25": "pm25",
        "pm10": "pm10",
        "no2": "no2",
        "so2": "so2",
        "co": "co",
        "o3": "o3"
    }

    column = column_map.get(
        pollutant
    )

    if column is None:
        raise ValueError(
            f"Unsupported pollutant: {pollutant}"
        )

    # --------------------------------------------------------
    # Level 1:
    # Same station + same month
    # --------------------------------------------------------

    station_data = historical_df[
        (
            historical_df["station"]
            == station_name
        )
        &
        (
            historical_df["month"]
            == month
        )
    ][column]

    station_data = pd.to_numeric(
        station_data,
        errors="coerce"
    ).dropna()

    station_data = station_data[
        station_data != 999
    ]

    if pollutant == "pm25":
        station_data = station_data[
            station_data <= 500
        ]

    if pollutant == "pm10":
        station_data = station_data[
            station_data <= 600
        ]

    if not station_data.empty:

        return float(
            station_data.median()
        )

    # --------------------------------------------------------
    # Level 2:
    # Mumbai-wide + same month
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

    if pollutant == "pm25":
        monthly_data = monthly_data[
            monthly_data <= 500
        ]

    if pollutant == "pm10":
        monthly_data = monthly_data[
            monthly_data <= 600
        ]

    if not monthly_data.empty:

        return float(
            monthly_data.median()
        )

    return None


# ============================================================
# Station Data Cleaning
# ============================================================

def clean_station_data(
    station,
    historical_df
):

    station_name = station.get(
        "station"
    )

    if not station_name:
        raise ValueError(
            "Station name is missing."
        )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    latitude = station.get(
        "latitude"
    )

    longitude = station.get(
        "longitude"
    )

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            f"Invalid coordinates for station: "
            f"{station_name}"
        )

    if not (
        -90 <= latitude <= 90
    ):
        raise ValueError(
            f"Invalid latitude for station "
            f"{station_name}: {latitude}"
        )

    if not (
        -180 <= longitude <= 180
    ):
        raise ValueError(
            f"Invalid longitude for station "
            f"{station_name}: {longitude}"
        )

    # --------------------------------------------------------
    # Find nearest historical station
    # --------------------------------------------------------

    station_mapping = (
        find_nearest_historical_station(
            latitude,
            longitude,
            historical_df
        )
    )

    if not station_mapping:
        raise ValueError(
            f"No historical station mapping found "
            f"for {station_name}"
        )

    historical_station_name = (
        station_mapping[
            "historical_station"
        ]
    )

    station_encoded = (
        station_mapping[
            "station_encoded"
        ]
    )

    distance_km = (
        station_mapping[
            "distance_km"
        ]
    )

    # --------------------------------------------------------
    # Month
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
    # Clean pollutants
    # --------------------------------------------------------

    cleaned_pollutants = {}

    imputation_flags = {}

    live_pollutants = (
        station.get(
            "pollutants",
            {}
        )
    )

    for pollutant in POLLUTANTS:

        live_value = live_pollutants.get(
            pollutant
        )

        # ----------------------------------------------------
        # Valid live value
        # ----------------------------------------------------

        if not is_invalid_value(
            live_value,
            pollutant
        ):

            cleaned_pollutants[
                pollutant
            ] = float(
                live_value
            )

            imputation_flags[
                pollutant
            ] = False

            continue

        # ----------------------------------------------------
        # Historical fallback
        # ----------------------------------------------------

        fallback = get_historical_median(
            historical_df,
            historical_station_name,
            pollutant,
            month
        )

        if fallback is None:

            raise ValueError(
                f"No fallback value available for "
                f"{pollutant} at station "
                f"{station_name}"
            )

        cleaned_pollutants[
            pollutant
        ] = fallback

        imputation_flags[
            pollutant
        ] = True

    # --------------------------------------------------------
    # AQI
    # --------------------------------------------------------

    aqi = station.get(
        "aqi"
    )

    if is_invalid_value(
        aqi,
        None
    ):

        cleaned_aqi = None

    else:

        cleaned_aqi = float(
            aqi
        )

    # --------------------------------------------------------
    # Return cleaned station
    # --------------------------------------------------------

    return {

        "station": station_name,

        "latitude": latitude,

        "longitude": longitude,

        "timestamp": station.get(
            "timestamp"
        ),

        "aqi": cleaned_aqi,

        "pollutants": cleaned_pollutants,

        "imputed": imputation_flags,

        "source": station.get(
            "source"
        ),

        "historical_station":
            historical_station_name,

        "station_encoded":
            station_encoded,

        "historical_latitude":
            station_mapping[
                "historical_latitude"
            ],

        "historical_longitude":
            station_mapping[
                "historical_longitude"
            ],

        "mapping_distance_km":
            distance_km,

        "is_fallback_station":
            station_name
            != historical_station_name
    }


# ============================================================
# WAQI Normalization
# ============================================================

def normalize_waqi_station(data):

    if not isinstance(
        data,
        dict
    ):
        raise ValueError(
            "Invalid WAQI station response."
        )

    city = data.get(
        "city"
    ) or {}

    iaqi = data.get(
        "iaqi"
    ) or {}

    time_data = data.get(
        "time"
    ) or {}

    geo = city.get(
        "geo"
    )

    if not isinstance(
        geo,
        (list, tuple)
    ) or len(geo) < 2:

        raise ValueError(
            "WAQI station does not contain "
            "valid coordinates."
        )

    def get_pollutant(
        key
    ):

        value = iaqi.get(
            key
        )

        if isinstance(
            value,
            dict
        ):

            return value.get(
                "v"
            )

        return None

    return {

        "station":
            city.get("name"),

        "latitude":
            geo[0],

        "longitude":
            geo[1],

        "timestamp":
            time_data.get("s"),

        "aqi":
            data.get("aqi"),

        "pollutants": {

            "pm25":
                get_pollutant("pm25"),

            "pm10":
                get_pollutant("pm10"),

            "no2":
                get_pollutant("no2"),

            "so2":
                get_pollutant("so2"),

            "co":
                get_pollutant("co"),

            "o3":
                get_pollutant("o3")
        },

        "source":
            "WAQI"
    }


# ============================================================
# CPCB Normalization
# ============================================================

def normalize_cpcb_records(
    records
):

    if not isinstance(
        records,
        list
    ):
        raise ValueError(
            "Invalid CPCB response format."
        )

    stations = {}

    for record in records:

        if not isinstance(
            record,
            dict
        ):
            continue

        station_name = record.get(
            "station"
        )

        if not station_name:
            continue

        if station_name not in stations:

            stations[
                station_name
            ] = {

                "station":
                    station_name,

                "latitude":
                    record.get(
                        "latitude"
                    ),

                "longitude":
                    record.get(
                        "longitude"
                    ),

                "timestamp":
                    record.get(
                        "last_update"
                    ),

                "aqi":
                    None,

                "pollutants":
                    {},

                "source":
                    "CPCB"
            }

        pollutant_id = record.get(
            "pollutant_id"
        )

        if not pollutant_id:
            continue

        pollutant_key = (
            POLLUTANT_MAPPING.get(
                str(
                    pollutant_id
                ).lower()
            )
        )

        if pollutant_key is None:
            continue

        value = record.get(
            "avg_value"
        )

        # IMPORTANT:
        # Pass pollutant_key here.
        if not is_invalid_value(
            value,
            pollutant_key
        ):

            stations[
                station_name
            ][
                "pollutants"
            ][
                pollutant_key
            ] = float(value)

    return list(
        stations.values()
    )

# ============================================================
# Google-based Mumbai Pollution
# ============================================================

async def get_current_mumbai_pollution():
    cache_key = "mumbai_pollution_20_stations"

    cached_data = get_cache(cache_key)

    if cached_data is not None:
        logger.info("Mumbai pollution map cache HIT")
        return cached_data

    logger.info("Mumbai pollution map cache MISS")

    historical_df = load_historical_data()

    # --------------------------------------------------------
    # Get unique Mumbai station locations
    # --------------------------------------------------------

    stations_df = (
        historical_df[
            [
                "station",
                "latitude",
                "longitude"
            ]
        ]
        .dropna()
        .drop_duplicates(
            subset=[
                "station"
            ]
        )
    )

    if stations_df.empty:

        raise RuntimeError(
            "No Mumbai station locations found "
            "in historical dataset."
        )

    logger.info(
        "Fetching Google AQI for %d Mumbai stations...",
        len(stations_df)
    )

    results = []

    # --------------------------------------------------------
    # Query Google for every station location
    # --------------------------------------------------------

    for _, station in stations_df.iterrows():

        station_name = station["station"]

        latitude = float(
            station["latitude"]
        )

        longitude = float(
            station["longitude"]
        )

        try:

            google_data = await get_current_air_quality(
                latitude=latitude,
                longitude=longitude
            )

            # ------------------------------------------------
            # Find India CPCB AQI
            # ------------------------------------------------

            india_aqi = None

            for index in google_data.get(
                "indexes",
                []
            ):

                if index.get("code") == "ind_cpcb":

                    india_aqi = index.get(
                        "aqi"
                    )

                    break

            if india_aqi is None:

                logger.warning(
                    "Google AQI unavailable for station '%s'",
                    station_name
                )

                continue

            # ------------------------------------------------
            # Build map record
            # ------------------------------------------------

            results.append({

                "station_name":
                    station_name,

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "aqi":
                    int(india_aqi),

                "color":
                    get_aqi_color(
                        india_aqi
                    )

            })

            logger.info(
                "Google AQI: %s = %s",
                station_name,
                india_aqi
            )

        except Exception as station_error:

            logger.warning(
                "Google AQI failed for station '%s': %s",
                station_name,
                station_error
            )

    # --------------------------------------------------------
    # Make sure at least one station worked
    # --------------------------------------------------------

    if not results:

        raise RuntimeError(
            "Google Air Quality API did not return "
            "usable AQI data for any Mumbai station."
        )

    logger.info(
        "Google successfully provided AQI for %d stations.",
        len(results)
    )

        # Cache the complete 20-station map response
    # for 15 minutes.
    set_cache(
        cache_key,
        results,
        ttl_seconds=15 * 60
    )

    return results