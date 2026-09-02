from typing import Dict


def classify_aqi(aqi: float) -> Dict:
    """
    Classify AQI according to the CPCB National AQI scale.
    """

    if aqi < 0:
        raise ValueError("AQI cannot be negative.")

    if aqi <= 50:
        category = "Good"
        risk_level = "Low"

    elif aqi <= 100:
        category = "Satisfactory"
        risk_level = "Low"

    elif aqi <= 200:
        category = "Moderate"
        risk_level = "Moderate"

    elif aqi <= 300:
        category = "Poor"
        risk_level = "High"

    elif aqi <= 400:
        category = "Very Poor"
        risk_level = "Very High"

    elif aqi <= 500:
        category = "Severe"
        risk_level = "Severe"

    else:
        category = "Severe"
        risk_level = "Severe"

    return {
        "aqi": aqi,
        "category": category,
        "risk_level": risk_level
    }