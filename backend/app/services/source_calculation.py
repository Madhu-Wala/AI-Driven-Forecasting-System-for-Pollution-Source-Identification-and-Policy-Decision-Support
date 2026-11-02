import math
from statistics import median


MAD_CONSTANT = 1.4826
MAX_Z_SCORE = 3.0
MIN_BASELINE_SAMPLES = 10


def safe_float(value):
    if value is None:
        return None

    try:
        number = float(value)

        if not math.isfinite(number):
            return None

        return number

    except (TypeError, ValueError):
        return None


def calculate_median_and_mad(values):
    clean_values = [
        number
        for value in values
        if (number := safe_float(value)) is not None
    ]

    if len(clean_values) < MIN_BASELINE_SAMPLES:
        return None

    median_value = median(clean_values)

    deviations = [
        abs(value - median_value)
        for value in clean_values
    ]

    mad_value = median(deviations)

    return {
        "median": median_value,
        "mad": mad_value,
        "sample_count": len(clean_values)
    }


def calculate_anomaly(current_value, baseline):
    """Calculate signed normalized pollutant deviation."""

    current_value = safe_float(current_value)

    if current_value is None or baseline is None:
        return None

    median_value = baseline["median"]
    mad_value = baseline["mad"]

    if mad_value is None or mad_value == 0:
        return None

    z_score = (
        current_value - median_value
    ) / (MAD_CONSTANT * mad_value)

    # Retain both positive and negative deviations.
    anomaly = max(
        -MAX_Z_SCORE,
        min(z_score, MAX_Z_SCORE)
    ) / MAX_Z_SCORE

    return round(anomaly, 4)


def calculate_coarse_pm(pm10, pm25):
    pm10 = safe_float(pm10)
    pm25 = safe_float(pm25)

    if pm10 is None or pm25 is None:
        return None

    return max(0, pm10 - pm25)


def calculate_category_score(anomaly_values):
    available_values = [
        value
        for item in anomaly_values
        if (value := safe_float(item)) is not None
    ]

    if not available_values:
        return None

    return round(
        sum(available_values) / len(available_values),
        4
    )


def calculate_category_scores(anomalies):
    return {
        "traffic": calculate_category_score([
            anomalies.get("no2"),
            anomalies.get("co")
        ]),

        "road_dust_construction": calculate_category_score([
            anomalies.get("pm10"),
            anomalies.get("coarse_pm")
        ]),

        "industry": calculate_category_score([
            anomalies.get("so2")
        ])
    }




def calculate_data_coverage(anomalies):
    total_indicators = len(anomalies)

    available_indicators = sum(
        value is not None
        for value in anomalies.values()
    )

    coverage = (
        available_indicators / total_indicators * 100
        if total_indicators > 0
        else 0
    )

    unavailable_indicators = [
        indicator
        for indicator, value in anomalies.items()
        if value is None
    ]

    return {
        "available_indicators": available_indicators,
        "total_indicators": total_indicators,
        "coverage_percentage": round(coverage, 2),
        "unavailable_indicators": unavailable_indicators
    }