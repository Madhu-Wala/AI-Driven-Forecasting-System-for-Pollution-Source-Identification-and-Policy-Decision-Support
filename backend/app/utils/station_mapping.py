import pandas as pd
from math import radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two latitude/longitude points in km.
    """

    R = 6371.0

    lat1, lon1, lat2, lon2 = map(
        radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def find_nearest_historical_station(
    latitude,
    longitude,
    historical_df
):
    """
    Find the geographically nearest station
    from the historical dataset.

    Returns:
        dict containing historical station,
        station_encoded and distance.
    """

    if historical_df.empty:
        raise ValueError("Historical dataset is empty.")

    required_columns = [
        "station",
        "latitude",
        "longitude",
        "station_encoded"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in historical_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in historical dataset: {missing_columns}"
        )

    # Keep only valid station coordinates
    stations = (
        historical_df[
            ["station", "latitude", "longitude", "station_encoded"]
        ]
        .dropna(subset=["latitude", "longitude"])
        .drop_duplicates(subset=["station"])
    )

    if stations.empty:
        raise ValueError(
            "No valid station coordinates found in historical dataset."
        )

    # Calculate distance from live WAQI station
    stations = stations.copy()

    stations["distance_km"] = stations.apply(
        lambda row: haversine_distance(
            latitude,
            longitude,
            row["latitude"],
            row["longitude"]
        ),
        axis=1
    )

    # Get nearest historical station
    nearest = stations.loc[
        stations["distance_km"].idxmin()
    ]

    return {
        "historical_station": nearest["station"],
        "station_encoded": int(nearest["station_encoded"]),
        "historical_latitude": float(nearest["latitude"]),
        "historical_longitude": float(nearest["longitude"]),
        "distance_km": round(float(nearest["distance_km"]), 3)
    }