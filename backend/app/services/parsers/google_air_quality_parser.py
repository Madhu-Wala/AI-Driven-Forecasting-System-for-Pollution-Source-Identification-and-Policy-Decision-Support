MOLECULAR_WEIGHTS = {
    "no2": 46.0055,
    "so2": 64.066,
    "co": 28.01,
    "o3": 47.9982,
    "nh3": 17.031
}

def parse_pollutants(pollutants):
    result = {}

    for pollutant in pollutants or []:
        code = pollutant.get("code")
        concentration = pollutant.get("concentration", {})

        if code:
            value = concentration.get("value")
            unit = concentration.get("units")

            # Convert ppb to µg/m³
            if value is not None and unit == "PARTS_PER_BILLION":
                molecular_weight = MOLECULAR_WEIGHTS.get(code)

                if molecular_weight:
                    value = float(value) * molecular_weight / 24.45

            result[code] = {
                "value": round(value, 2) if value is not None else None,
                "unit": "µg/m³"
            }

    return result


def parse_aqi(indexes):
    india_aqi = None
    universal_aqi = None

    for index in indexes or []:
        if index.get("code") == "ind_cpcb":
            india_aqi = {
                "aqi": index.get("aqi"),
                "display": index.get("aqiDisplay"),
                "category": index.get("category"),
                "dominant_pollutant": index.get("dominantPollutant")
            }

        elif index.get("code") == "uaqi":
            universal_aqi = {
                "aqi": index.get("aqi"),
                "display": index.get("aqiDisplay"),
                "category": index.get("category"),
                "dominant_pollutant": index.get("dominantPollutant")
            }

    return india_aqi, universal_aqi


def parse_current_air_quality(data):
    india_aqi, universal_aqi = parse_aqi(
        data.get("indexes")
    )

    return {
        "source": "Google Air Quality API",
        "model_based": True,
        "region_code": data.get("regionCode"),
        "timestamp": data.get("dateTime"),

        "aqi": (
            india_aqi["aqi"]
            if india_aqi
            else None
        ),

        "aqi_display": (
            india_aqi["display"]
            if india_aqi
            else None
        ),

        "aqi_scale": "NAQI (IN)",

        "category": (
            india_aqi["category"]
            if india_aqi
            else None
        ),

        "dominant_pollutant": (
            india_aqi["dominant_pollutant"]
            if india_aqi
            else None
        ),

        "universal_aqi": (
            universal_aqi["aqi"]
            if universal_aqi
            else None
        ),

        "pollutants": parse_pollutants(
            data.get("pollutants")
        )
    }