import os

import joblib
import shap
import pandas as pd

from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

MODEL_PATH = os.getenv("SHAP_MODEL_PATH")


# =========================================================
# LOAD MODEL
# =========================================================

if not MODEL_PATH:
    raise RuntimeError(
        "SHAP_MODEL_PATH is not configured in .env"
    )


model_package = joblib.load(MODEL_PATH)


# The saved PKL contains:
# {
#     "model": XGBRegressor(...),
#     "features": [
#         "pm25",
#         "pm10",
#         "no2",
#         "so2",
#         "co",
#         "o3"
#     ]
# }

model_shap = model_package["model"]

FEATURES = model_package["features"]


# =========================================================
# SHAP EXPLAINER
# =========================================================

explainer = shap.Explainer(model_shap)


# =========================================================
# GET POLLUTANT VALUE
# =========================================================

def get_pollutant_value(
    pollutants,
    pollutant_name
):
    pollutant = pollutants.get(
        pollutant_name
    )

    if not pollutant:
        return None

    return pollutant.get("value")


# =========================================================
# EXPLAIN CURRENT POLLUTION
# =========================================================

def explain_current_pollution(
    pollutants
):

    # -----------------------------------------------------
    # Create one-row dataframe
    # -----------------------------------------------------

    input_data = pd.DataFrame([{
        feature: get_pollutant_value(
            pollutants,
            feature
        )
        for feature in FEATURES
    }])

    # -----------------------------------------------------
    # Check missing values
    # -----------------------------------------------------

    missing_features = [
        feature
        for feature in FEATURES
        if pd.isna(
            input_data.iloc[0][feature]
        )
    ]

    if missing_features:

        raise ValueError(
            "Missing pollutant values: "
            + ", ".join(missing_features)
        )

    # -----------------------------------------------------
    # Predict AQI using saved model
    # -----------------------------------------------------

    predicted_aqi = model_shap.predict(
        input_data
    )[0]

    # -----------------------------------------------------
    # Calculate SHAP values
    # -----------------------------------------------------

    shap_result = explainer(
        input_data
    )

    shap_values = shap_result.values[0]

    # -----------------------------------------------------
    # Build contribution list
    # -----------------------------------------------------

    contributions = []

    for feature, value in zip(
        FEATURES,
        shap_values
    ):

        contributions.append({
            "pollutant": feature,
            "shap_value": round(
                float(value),
                2
            ),
            "direction": (
                "increases AQI"
                if value > 0
                else "decreases AQI"
                if value < 0
                else "neutral"
            )
        })

    # -----------------------------------------------------
    # Sort by magnitude
    # -----------------------------------------------------

    contributions.sort(
        key=lambda item: abs(
            item["shap_value"]
        ),
        reverse=True
    )

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {
        "predicted_aqi": round(
            float(predicted_aqi),
            2
        ),
        "contributions": contributions
    }