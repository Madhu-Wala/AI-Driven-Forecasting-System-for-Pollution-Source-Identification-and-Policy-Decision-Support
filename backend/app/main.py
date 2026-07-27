from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.station import router as station_router

app=FastAPI(
    title="AI-Driven Forecasting System for Pollution Source Identification and Policy Decision Support",
    description="Backend APIs for AQI Monitoring, Forecasting, Source Attribution and Policy Recommendation",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(station_router) 

@app.get("/")
def root():
    return {"message": "Ganpati Bappa Morya !! 🙏 Backend is running!"}