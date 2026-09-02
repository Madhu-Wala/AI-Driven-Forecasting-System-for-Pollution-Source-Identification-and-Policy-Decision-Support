def build_advisory_query(
    age_group: str,
    health_conditions: list[str],
    activity_level: str,
    aqi: float,
    aqi_category: str
) -> str:

    conditions = ", ".join(health_conditions) if health_conditions else "None"

    query = (
        f"Citizen health advisory. "
        f"AQI is {aqi}, category is {aqi_category}. "
        f"Age group: {age_group}. "
        f"Health conditions: {conditions}. "
        f"Activity level: {activity_level}. "
        f"Relevant precautions for outdoor exposure, "
        f"physical activity, respiratory health, "
        f"indoor air quality, protective measures, "
        f"and warning symptoms."
    )

    return query