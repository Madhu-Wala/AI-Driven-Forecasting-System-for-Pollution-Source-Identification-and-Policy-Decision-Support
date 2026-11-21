from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.station import router as station_router
from app.api.pollution import router as pollution_router
from app.api.weather import router as weather_router
from app.api.prediction import router as prediction_router
from app.api.air_quality import router as air_quality_router
from app.api.shap import router as shap_router
from app.api.advisory import router as advisory_router
from app.api.source_identification import router as source_identification_router
from app.api.analytics import router as analytics_router
from app.api.hotspots import router as hotspots_router
from app.api.policy import router as policy_router
from app.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(
    title="AI-Driven Forecasting System for Pollution Source Identification and Policy Decision Support",
    description="Backend APIs for AQI Monitoring, Forecasting, Source Attribution and Policy Recommendation",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(health_router)
app.include_router(station_router) 
app.include_router(pollution_router)
app.include_router(weather_router)
app.include_router(prediction_router) # Old
app.include_router(air_quality_router) # prediction
app.include_router(advisory_router)
app.include_router(source_identification_router)
app.include_router(analytics_router)
app.include_router(hotspots_router)
app.include_router(policy_router)

@app.get("/")
def root():
    return {"message": "Ganpati Bappa Morya !! 🙏 Backend is running!"}