import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import csv
import os
from functools import lru_cache
from app.database.connection import get_database_connection

from app.services.source_calculation import (
    safe_float,
    calculate_median_and_mad,
    calculate_anomaly,
    calculate_coarse_pm,
    calculate_category_scores,
    calculate_data_coverage,
)

from app.services.providers.weather_provider import (
    get_weather_for_date
)


logger = logging.getLogger(__name__)

IST = ZoneInfo("Asia/Kolkata")
HISTORY_DAYS = 30

# ============================================================
# Station Coordinate Mapping
# ============================================================

STATION_MAPPING_PATH = os.getenv(
    "STATION_MAPPING_PATH",
    r"E:\Capstone\data\stations\stations.csv"
)


@lru_cache(maxsize=1)
def load_station_coordinate_mapping():
    """
    Load station coordinates using station_encoded
    from the existing stations.csv file.
    """

    if not os.path.isfile(STATION_MAPPING_PATH):
        raise FileNotFoundError(
            f"Station mapping file not found: {STATION_MAPPING_PATH}"
        )

    station_mapping = {}

    with open(
        STATION_MAPPING_PATH,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "station_encoded",
            "latitude",
            "longitude"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Station mapping CSV must contain: "
                "station_encoded, latitude, longitude"
            )

        for row in reader:

            encoded = int(row["station_encoded"])

            station_mapping[encoded] = {
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "station": row.get("station"),
                "display_name": row.get("display_name")
            }

    logger.info(
        "Loaded coordinates for %d stations",
        len(station_mapping)
    )

    return station_mapping


def get_station_coordinates(station_id):
    """
    Resolve station_0, station_1, etc. to CSV coordinates.
    """

    try:
        station_encoded = int(
            station_id.replace("station_", "")
        )

        mapping = load_station_coordinate_mapping()

        return mapping.get(station_encoded)

    except (ValueError, AttributeError):
        logger.error(
            "Invalid station ID format: %s",
            station_id
        )
        return None

def fetch_historical_pollution_data():
    """Fetch the last 30 days of hourly observations."""

    current_ist = datetime.now(IST)

    cutoff_ist = (
        current_ist - timedelta(days=HISTORY_DAYS)
    ).replace(tzinfo=None)

    query = """
        SELECT
            id,
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
        FROM public.air_quality_data
        WHERE timestamp >= %s
          AND station_id IS NOT NULL
        ORDER BY station_id, timestamp ASC, id ASC;
    """

    connection = None

    try:
        connection = get_database_connection()

        with connection.cursor() as cursor:
            cursor.execute(query, (cutoff_ist,))
            rows = cursor.fetchall()

        columns = [
            "id",
            "station_id",
            "station_name",
            "latitude",
            "longitude",
            "timestamp",
            "aqi",
            "aqi_category",
            "pm25",
            "pm10",
            "no2",
            "so2",
            "co",
            "o3",
            "source",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        if connection is not None:
            connection.close()


def get_latest_station_records(records):
    """Get the latest observation for each station ID."""

    latest_records = {}

    for record in records:
        station_id = record["station_id"]
        timestamp = record["timestamp"]

        if timestamp is None:
            continue

        existing = latest_records.get(station_id)

        if (
            existing is None
            or timestamp > existing["timestamp"]
            or (
                timestamp == existing["timestamp"]
                and record["id"] > existing["id"]
            )
        ):
            latest_records[station_id] = record

    return list(latest_records.values())


def generate_station_baselines(
    station_id,
    current_record,
    historical_records,
):
    """Generate same-month historical baselines."""

    current_timestamp = current_record["timestamp"]

    pollutant_history = {
        "pm25": [],
        "pm10": [],
        "no2": [],
        "so2": [],
        "co": [],
        "coarse_pm": [],
    }

    for record in historical_records:

        if record["station_id"] != station_id:
            continue

        timestamp = record["timestamp"]

        if timestamp is None:
            continue

        if (
            timestamp.year != current_timestamp.year
            or timestamp.month != current_timestamp.month
        ):
            continue

        if timestamp >= current_timestamp:
            continue

        pm25 = safe_float(record["pm25"])
        pm10 = safe_float(record["pm10"])

        for pollutant in [
            "pm25", "pm10", "no2", "so2", "co"
        ]:
            value = safe_float(record[pollutant])

            if value is not None:
                pollutant_history[pollutant].append(value)

        coarse_pm = calculate_coarse_pm(pm10, pm25)

        if coarse_pm is not None:
            pollutant_history["coarse_pm"].append(coarse_pm)

    return {
        pollutant: calculate_median_and_mad(values)
        for pollutant, values in pollutant_history.items()
    }


def generate_pollutant_anomalies(current_record, baselines):
    """Calculate signed normalized pollutant anomalies."""

    pm25 = safe_float(current_record["pm25"])
    pm10 = safe_float(current_record["pm10"])

    current_coarse_pm = calculate_coarse_pm(pm10, pm25)

    current_values = {
        "no2": safe_float(current_record["no2"]),
        "co": safe_float(current_record["co"]),
        "pm10": pm10,
        "coarse_pm": current_coarse_pm,
        "so2": safe_float(current_record["so2"]),
    }

    anomalies = {}

    for pollutant, current_value in current_values.items():
        anomalies[pollutant] = calculate_anomaly(
            current_value,
            baselines[pollutant],
        )

    return anomalies



def interpret_weather_context(weather):
    """
    Interpret hourly meteorological conditions.

    These are contextual observations, not source
    attribution scores or pollutant correction factors.
    """

    precipitation = safe_float(
        weather.get("precipitation")
    )

    humidity = safe_float(
        weather.get("relative_humidity_2m")
    )

    temperature = safe_float(
        weather.get("temperature_2m")
    )

    wind_speed = safe_float(
        weather.get("wind_speed_10m")
    )

    wind_direction = safe_float(
        weather.get("wind_direction_10m")
    )

    pressure = safe_float(
        weather.get("pressure_msl")
    )

    factors = []

    if precipitation is not None:

        if precipitation >= 1:
            factors.append(
                "Rainfall during this hour may contribute "
                "to particle washout and road dust suppression."
            )

        elif precipitation == 0:
            factors.append(
                "No rainfall was recorded during this hour."
            )

        else:
            factors.append(
                "Light precipitation was recorded during "
                "this hour; its dust suppression effect "
                "may be limited."
            )

    if humidity is not None:

        if humidity >= 80:
            factors.append(
                "High relative humidity may influence "
                "hygroscopic particle growth."
            )

        elif humidity < 40:
            factors.append(
                "Relatively low humidity was recorded."
            )

        else:
            factors.append(
                "Moderate relative humidity was recorded."
            )

    if temperature is not None:
        factors.append(
            f"Temperature was {temperature:.1f} °C."
        )

    if wind_speed is not None:

        if wind_speed < 2:
            factors.append(
                "Low wind speed may favour pollutant "
                "accumulation due to limited ventilation."
            )

        elif wind_speed >= 15:
            factors.append(
                "High wind speed may increase dispersion, "
                "transport or dust resuspension."
            )

        else:
            factors.append(
                "Moderate wind conditions may influence "
                "pollutant dispersion and transport."
            )

    if wind_direction is not None:
        factors.append(
            f"Wind direction was {wind_direction:.1f} degrees."
        )

    return {
        "precipitation_mm": precipitation,
        "relative_humidity_percent": humidity,
        "temperature_celsius": temperature,
        "wind_speed_mps": wind_speed,
        "wind_direction_degrees": wind_direction,
        "pressure_msl_hpa": pressure,
        "interpretation": factors,
        "note": (
            "Hourly weather data provides meteorological "
            "context corresponding to the pollution "
            "observation hour. It does not independently "
            "identify pollution sources or directly correct "
            "pollutant concentrations."
        )
    }


def get_station_weather(current_record, weather_cache):
    """
    Fetch hourly weather for the same observation hour
    using station coordinates from stations.csv.
    """

    station_id = current_record.get("station_id")
    observation_timestamp = current_record.get("timestamp")

    if not station_id or observation_timestamp is None:
        return None

    try:

        # Resolve coordinates from stations.csv.
        station_coordinates = get_station_coordinates(
            station_id
        )

        if station_coordinates is None:
            logger.warning(
                "No coordinate mapping found for station %s",
                station_id
            )
            return None

        latitude = station_coordinates["latitude"]
        longitude = station_coordinates["longitude"]

        # Normalize timestamp to the same IST hour.
        if isinstance(observation_timestamp, str):
            observation_timestamp = datetime.fromisoformat(
                observation_timestamp.replace("Z", "+00:00")
            )

        if observation_timestamp.tzinfo is not None:
            observation_timestamp = (
                observation_timestamp.astimezone(IST)
            )

        else:
            observation_timestamp = (
                observation_timestamp.replace(tzinfo=IST)
            )

        observation_hour = observation_timestamp.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        weather_time = observation_hour.strftime(
            "%Y-%m-%dT%H:%M"
        )

        # Cache by station and observation hour.
        cache_key = (
            station_id,
            weather_time
        )

        if cache_key in weather_cache:
            return weather_cache[cache_key]

        # Fetch matching hourly weather.
        weather = get_weather_for_date(
            latitude=latitude,
            longitude=longitude,
            target_timestamp=observation_hour
        )

        if weather is None:
            return None

        result = {
            "source": "Open-Meteo",
            "date": observation_hour.date().isoformat(),
            "observation_hour": weather_time,
            **interpret_weather_context(weather)
        }

        # Cache only successful responses.
        weather_cache[cache_key] = result

        return result

    except Exception:

        logger.exception(
            "Hourly weather retrieval failed for station %s",
            station_id
        )

        # Do not cache failures.
        # A later request can try again.
        return None

    
def get_source_signal_label(score):
    """Convert signed anomaly scores into citizen-friendly labels."""

    score = safe_float(score)

    if score is None:
        return "Insufficient data"

    if score > 0:
        return "Above usual levels"

    if score < 0:
        return "Below usual levels"

    return "Around usual levels"

def analyse_station(
    current_record,
    historical_records,
    weather_cache
):
    """Perform source identification for one station."""

    station_id = current_record["station_id"]

    baselines = generate_station_baselines(
        station_id,
        current_record,
        historical_records,
    )

    anomalies = generate_pollutant_anomalies(
        current_record,
        baselines,
    )

    category_scores = calculate_category_scores(anomalies)

    source_scores = category_scores

    source_scores_display = {
        category: (
            0.01 if score == 0 else score
        ) if score is not None else None
        for category, score in source_scores.items()
    }

    source_signal_labels = {
        category: get_source_signal_label(score)
        for category, score in source_scores.items()
    }

    coverage = calculate_data_coverage(anomalies)

    baseline_samples = {
        pollutant: (
            baseline["sample_count"]
            if baseline is not None
            else 0
        )
        for pollutant, baseline in baselines.items()
    }

    pm25 = safe_float(current_record["pm25"])
    pm10 = safe_float(current_record["pm10"])

    current_pollutants = {
        "pm25": pm25,
        "pm10": pm10,
        "coarse_pm": calculate_coarse_pm(pm10, pm25),
        "no2": safe_float(current_record["no2"]),
        "so2": safe_float(current_record["so2"]),
        "co": safe_float(current_record["co"]),
        "o3": safe_float(current_record["o3"]),
    }

    weather_context = get_station_weather(
        current_record,
        weather_cache
    )

    has_positive_anomaly = any(
        score is not None and score > 0
        for score in source_scores.values()
    )

    status = (
        "Positive pollutant anomaly detected"
        if has_positive_anomaly
        else "No positive pollutant anomaly detected"
    )

    return {
        "station_id": station_id,
        "station_name": current_record["station_name"],
        "latitude": safe_float(current_record["latitude"]),
        "longitude": safe_float(current_record["longitude"]),
        "timestamp": current_record["timestamp"].isoformat(),

        "current_pollutants": current_pollutants,

        "pollutant_anomalies": anomalies,

        "category_scores": category_scores,

        "source_scores": source_scores,

        "source_scores_display": source_scores_display,

        "source_signal_labels": source_signal_labels,
        "weather_context": weather_context,
        #"weather_context": None,

        "data_coverage": coverage,

        "baseline_sample_counts": baseline_samples,

        "status": status,

        "interpretation": (
            "Source scores represent signed normalized pollutant "
            "deviations from historical baselines for Traffic, "
            "Road Dust / Construction and Industry. Positive values "
            "indicate above-baseline pollutant signals, while negative "
            "values indicate below-baseline signals. These are "
            "heuristic indicators and do not represent actual emission "
            "contribution percentages or confirmed pollution sources. "
            "Weather information provides additional meteorological "
            "context."
        ),
    }


def get_all_source_identification_results():
    """Generate source identification results for all stations."""

    historical_records = fetch_historical_pollution_data()

    if not historical_records:
        return []

    latest_records = get_latest_station_records(
        historical_records
    )

    results = []

    # Cache is shared across all stations in this API call.
    weather_cache = {}

    for current_record in latest_records:
        try:
            result = analyse_station(
                current_record,
                historical_records,
                weather_cache
            )

            results.append(result)

        except Exception:
            logger.exception(
                "Source identification failed for station %s",
                current_record["station_id"]
            )

    return results

def get_source_identification_by_station(station_id):
    """Return source identification for a specific station only."""

    historical_records = fetch_historical_pollution_data()

    if not historical_records:
        return None

    # Filter historical data to the requested station only.
    station_records = [
        record
        for record in historical_records
        if record["station_id"] == station_id
    ]

    if not station_records:
        return None

    # Find the latest observation for this station.
    current_record = get_latest_station_records(station_records)[0]

    # Analyse only this station.
    return analyse_station(
        current_record,
        station_records,
        weather_cache={}
    )
