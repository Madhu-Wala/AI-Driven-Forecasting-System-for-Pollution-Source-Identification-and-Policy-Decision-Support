
import os
import joblib
import pandas as pd
from dotenv import load_dotenv

from app.utils.station_mapping import find_nearest_historical_station


load_dotenv()


# =========================================================
# Configuration
# =========================================================

MODEL_PATH = os.getenv("AQI_MODEL_PATH")
HISTORICAL_DATASET = os.getenv("HISTORICAL_DATASET_PATH")


# =========================================================
# Load LightGBM model
# =========================================================

if not MODEL_PATH:
    raise RuntimeError(
        "AQI_MODEL_PATH is not configured in .env"
    )

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"AQI model not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# =========================================================
# Load historical dataset
# =========================================================

def load_historical_data():

    if not HISTORICAL_DATASET:
        raise RuntimeError(
            "HISTORICAL_DATASET_PATH is not configured in .env"
        )

    if not os.path.exists(HISTORICAL_DATASET):
        raise FileNotFoundError(
            f"Historical dataset not found: {HISTORICAL_DATASET}"
        )

    df = pd.read_csv(HISTORICAL_DATASET)

    required_columns = [
        "station",
        "latitude",
        "longitude",
        "station_encoded"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Historical dataset missing columns: {missing}"
        )

    return df


# =========================================================
# Prepare model input
# =========================================================

def prepare_prediction_input(
    weather_forecast,
    latitude,
    longitude,
    current_aqi,
    historical_df
):
    """
    Prepare the exact 13 features used during
    LightGBM training.

    AQI_lag1 = latest observed AQI available
                at prediction time.

    The same current AQI is used as the lag-1
    baseline for each future forecast day.
    """

    if not weather_forecast:
        raise ValueError(
            "Weather forecast is empty."
        )

    if current_aqi is None:
        raise ValueError(
            "Current AQI is required for AQI_lag1."
        )

    # -----------------------------------------------------
    # Validate current AQI
    # -----------------------------------------------------

    try:
        current_aqi = float(current_aqi)

    except (TypeError, ValueError):

        raise ValueError(
            f"Invalid current AQI value: {current_aqi}"
        )

    if current_aqi < 0:

        raise ValueError(
            f"Current AQI cannot be negative: {current_aqi}"
        )


    # -----------------------------------------------------
    # Find nearest historical station
    # -----------------------------------------------------

    station_mapping = find_nearest_historical_station(
        latitude,
        longitude,
        historical_df
    )

    if not station_mapping:

        raise ValueError(
            "No historical station mapping found."
        )


    # -----------------------------------------------------
    # Get station encoded value
    # -----------------------------------------------------

    station_encoded = station_mapping.get(
        "station_encoded"
    )

    if station_encoded is None:

        raise ValueError(
            "Nearest historical station does not have "
            "a station_encoded value."
        )

    station_encoded = int(station_encoded)


    # -----------------------------------------------------
    # Create prediction rows
    # -----------------------------------------------------

    rows = []

    for weather in weather_forecast:

        row = {

            # ---------------------------------------------
            # Weather features
            # ---------------------------------------------

            "temperature_2m_mean":
                weather["temperature_2m_mean"],

            "relative_humidity_2m_mean":
                weather["relative_humidity_2m_mean"],

            "wind_speed_10m_mean":
                weather["wind_speed_10m_mean"],

            "wind_speed_10m_max":
                weather["wind_speed_10m_max"],

            "wind_direction_10m_dominant":
                weather["wind_direction_10m_dominant"],

            "pressure_msl_mean":
                weather["pressure_msl_mean"],

            "precipitation_sum":
                weather["precipitation_sum"],


            # ---------------------------------------------
            # Time features
            # ---------------------------------------------

            "month":
                weather["month"],

            "dayofyear":
                weather["dayofyear"],


            # ---------------------------------------------
            # Spatial features
            # ---------------------------------------------

            "latitude":
                float(latitude),

            "longitude":
                float(longitude),

            "station_encoded":
                station_encoded,


            # ---------------------------------------------
            # Previous AQI
            # ---------------------------------------------

            "AQI_lag1":
                current_aqi
        }

        rows.append(row)


    prediction_df = pd.DataFrame(rows)


    return prediction_df, station_mapping


# =========================================================
# Predict future AQI
# =========================================================

def predict_future_aqi(
    weather_forecast,
    latitude,
    longitude,
    current_aqi
):

    # -----------------------------------------------------
    # Load historical data
    # -----------------------------------------------------

    historical_df = load_historical_data()


    # -----------------------------------------------------
    # Prepare exact model input
    # -----------------------------------------------------

    prediction_df, station_mapping = (
        prepare_prediction_input(
            weather_forecast=weather_forecast,
            latitude=latitude,
            longitude=longitude,
            current_aqi=current_aqi,
            historical_df=historical_df
        )
    )


    # =====================================================
    # EXACT 13 FEATURES USED DURING TRAINING
    # =====================================================

    feature_columns = [

        "temperature_2m_mean",

        "relative_humidity_2m_mean",

        "wind_speed_10m_mean",

        "wind_speed_10m_max",

        "wind_direction_10m_dominant",

        "pressure_msl_mean",

        "precipitation_sum",

        "month",

        "dayofyear",

        "latitude",

        "longitude",

        "station_encoded",

        "AQI_lag1"
    ]


    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    missing_features = [
        col
        for col in feature_columns
        if col not in prediction_df.columns
    ]

    if missing_features:

        raise ValueError(
            "Prediction input is missing features: "
            f"{missing_features}"
        )


    # -----------------------------------------------------
    # Create model input
    # -----------------------------------------------------

    X = prediction_df[feature_columns]


    print("\nModel input:")
    print(X)

    print("\nModel input columns:")
    print(X.columns.tolist())

    print("\nNumber of model features:")
    print(X.shape[1])


    # -----------------------------------------------------
    # Predict
    # -----------------------------------------------------

    predictions = model.predict(X)


    prediction_df["predicted_AQI"] = predictions


    # AQI cannot be negative
    prediction_df["predicted_AQI"] = (
        prediction_df["predicted_AQI"]
        .clip(lower=0)
    )


    # -----------------------------------------------------
    # Format response
    # -----------------------------------------------------

    forecast = []

    for index, row in prediction_df.iterrows():

        forecast.append({

            "date":
                weather_forecast[index]["date"],

            "predicted_AQI":
                round(
                    float(row["predicted_AQI"]),
                    2
                )
        })


    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "current_aqi":
            round(
                float(current_aqi),
                2
            ),

        "historical_station":
            station_mapping["historical_station"],

        "station_encoded":
            station_mapping["station_encoded"],

        "mapping_distance_km":
            station_mapping["distance_km"],

        "forecast":
            forecast
    }