def build_policy_query(station_data: dict):

    station_id = station_data.get("station_id", "Unknown")
    station_name = station_data.get("station_name", "Unknown")

    aqi = station_data.get("aqi")
    aqi_category = station_data.get("aqi_category")

    category_scores = station_data.get("category_scores", {})
    anomalies = station_data.get("pollutant_anomalies", {})

    query_parts = [
        "Policy decision support for Mumbai air pollution.",
        f"Station ID: {station_id}.",
        f"Station name: {station_name}."
    ]

    if aqi is not None:
        query_parts.append(f"Current AQI: {aqi}.")

    if aqi_category:
        query_parts.append(f"AQI category: {aqi_category}.")

    if category_scores:
        query_parts.append(
            f"Potential pollution source signals: {category_scores}."
        )

    if anomalies:
        query_parts.append(
            f"Pollutant anomaly observations: {anomalies}."
        )

    query_parts.append(
        "Find relevant Mumbai and national air pollution policies, "
        "NAAQS standards, GRAP actions, mitigation measures, "
        "implementation guidance, and responsible authorities. "
        "Prioritize interventions relevant to the identified "
        "pollution source signals."
    )

    return " ".join(query_parts)