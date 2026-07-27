from fastapi import APIRouter

router=APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "AI-Driven Forecasting System for Pollution Source Identification and Policy Decision Support is running smoothly."
    }
