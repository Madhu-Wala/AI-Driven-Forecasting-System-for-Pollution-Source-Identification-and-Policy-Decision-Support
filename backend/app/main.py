from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.station import router as station_router
from app.api.pollution import router as pollution_router
from app.api.weather import router as weather_router
from app.api.prediction import router as prediction_router
from app.api.air_quality import router as air_quality_router
from app.api.shap import router as shap_router

app=FastAPI(
    title="AI-Driven Forecasting System for Pollution Source Identification and Policy Decision Support",
    description="Backend APIs for AQI Monitoring, Forecasting, Source Attribution and Policy Recommendation",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(station_router) 
app.include_router(pollution_router)
app.include_router(weather_router)
app.include_router(prediction_router)
app.include_router(air_quality_router)
app.include_router(shap_router)

@app.get("/")
def root():
    return {"message": "Ganpati Bappa Morya !! 🙏 Backend is running!"}