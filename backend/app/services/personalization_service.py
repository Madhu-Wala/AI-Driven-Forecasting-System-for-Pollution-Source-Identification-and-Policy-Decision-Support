from typing import Dict, List


def generate_personalized_risk(
    age_group: str,
    health_conditions: List[str],
    activity_level: str,
    aqi: float
) -> Dict:

    if aqi < 0:
        raise ValueError("AQI cannot be negative.")

    # Normalize inputs
    age_group = age_group.strip()
    activity_level = activity_level.strip()

    conditions = [
        condition.strip().lower()
        for condition in health_conditions
    ]

    # Base risk from AQI
    if aqi <= 50:
        risk_level = "Low"

    elif aqi <= 100:
        risk_level = "Low"

    elif aqi <= 200:
        risk_level = "Moderate"

    elif aqi <= 300:
        risk_level = "High"

    elif aqi <= 400:
        risk_level = "Very High"

    else:
        risk_level = "Severe"

    risk_score = 0

    # -------------------------------------------------
    # AGE FACTOR
    # -------------------------------------------------

    if age_group == "65+ years":
        risk_score += 2

    elif age_group == "51-65 years":
        risk_score += 1

    # -------------------------------------------------
    # HEALTH CONDITION FACTOR
    # -------------------------------------------------

    respiratory_conditions = {
        "asthma",
        "copd / chronic lung condition",
        "other respiratory condition"
    }

    cardiovascular_conditions = {
        "heart / cardiovascular condition"
    }

    sensitive_conditions = {
        "diabetes",
        "allergies / sinusitis",
        "pregnancy"
    }

    for condition in conditions:

        if condition in respiratory_conditions:
            risk_score += 2

        elif condition in cardiovascular_conditions:
            risk_score += 2

        elif condition in sensitive_conditions:
            risk_score += 1

    # -------------------------------------------------
    # ACTIVITY FACTOR
    # -------------------------------------------------

    if activity_level == "Heavy Activity":
        risk_score += 2

    elif activity_level == "Moderate Activity":
        risk_score += 1

    # -------------------------------------------------
    # AQI + PERSONAL FACTORS
    # -------------------------------------------------

    if aqi <= 50:
        base_message = "Air quality is good."

    elif aqi <= 100:
        base_message = "Air quality is satisfactory."

    elif aqi <= 200:
        base_message = "Air quality is moderate. Sensitive individuals may need additional precautions."

    elif aqi <= 300:
        base_message = "Air quality is poor. Outdoor activity should be reduced."

    elif aqi <= 400:
        base_message = "Air quality is very poor. Outdoor exertion should be avoided."

    else:
        base_message = "Air quality is severe. Avoid outdoor exposure as much as possible."

    # -------------------------------------------------
    # PERSONALIZED RISK
    # -------------------------------------------------

    if risk_score >= 5:
        personalized_risk = "Very High"

    elif risk_score >= 3:
        personalized_risk = "High"

    elif risk_score >= 1:
        personalized_risk = "Moderate"

    else:
        personalized_risk = risk_level

    # -------------------------------------------------
    # ACTIVITY RECOMMENDATION
    # -------------------------------------------------

    if aqi <= 100:
        activity_recommendation = (
            "Outdoor activity may generally be continued, "
            "while remaining attentive to personal symptoms."
        )

    elif aqi <= 200:
        if (
            activity_level == "Heavy Activity"
            or any(condition in respiratory_conditions for condition in conditions)
        ):
            activity_recommendation = (
                "Consider reducing strenuous outdoor activity "
                "and prefer indoor alternatives."
            )
        else:
            activity_recommendation = (
                "Reduce prolonged or strenuous outdoor activity."
            )

    elif aqi <= 300:
        activity_recommendation = (
            "Avoid or significantly reduce strenuous outdoor activity."
        )

    else:
        activity_recommendation = (
            "Avoid outdoor exertion and prefer indoor activities."
        )

    return {
        "personalized_risk": personalized_risk,
        "risk_score": risk_score,
        "summary": base_message,
        "activity_recommendation": activity_recommendation
    }