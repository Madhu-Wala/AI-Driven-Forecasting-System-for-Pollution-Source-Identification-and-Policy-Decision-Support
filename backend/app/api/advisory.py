from fastapi import APIRouter, HTTPException

from app.models.advisory import AdvisoryRequest
from app.services.air_quality_service import get_current
from app.services.aqi_service import classify_aqi
from app.services.personalization_service import generate_personalized_risk
from app.rag.advisory_retriever import retrieve_advisory_evidence
from app.services.advisory_llm_service import generate_llm_advisory

from app.services.advisory_validator import validate_advisory


router = APIRouter(
    prefix="/api/advisory",
    tags=["Personalized Health Advisory"]
)


@router.post("/")
async def generate_advisory(request: AdvisoryRequest):

    try:
        # --------------------------------------------------
        # 1. Get current air quality
        # --------------------------------------------------

        air_quality = await get_current(
            latitude=request.latitude,
            longitude=request.longitude
        )

        aqi = air_quality["aqi"]

        # --------------------------------------------------
        # 2. Classify AQI using CPCB scale
        # --------------------------------------------------

        aqi_info = classify_aqi(aqi)

        # --------------------------------------------------
        # 3. Deterministic personalization
        # --------------------------------------------------

        personalized_risk = generate_personalized_risk(
            age_group=request.age_group,
            health_conditions=request.health_conditions,
            activity_level=request.activity_level,
            aqi=aqi
        )

        # --------------------------------------------------
        # 4. Retrieve relevant RAG evidence
        # --------------------------------------------------

        rag_result = retrieve_advisory_evidence(
            age_group=request.age_group,
            health_conditions=request.health_conditions,
            activity_level=request.activity_level,
            aqi=aqi,
            aqi_category=aqi_info["category"],
            k=3
        )

        # --------------------------------------------------
        # 5. Generate personalized LLM advisory
        # --------------------------------------------------

        llm_advisory = generate_llm_advisory(
            age_group=request.age_group,
            health_conditions=request.health_conditions,
            activity_level=request.activity_level,
            aqi=aqi,
            aqi_category=aqi_info["category"],
            personalized_risk=personalized_risk,
            documents=rag_result["documents"]
        )

        llm_advisory = validate_advisory(
            advisory=llm_advisory,
            aqi=aqi,
            aqi_category=aqi_info["category"],
            personalized_risk=personalized_risk,
        )

        # --------------------------------------------------
        # 6. Return complete response
        # --------------------------------------------------

        return {
            "user_profile": {
                "age_group": request.age_group,
                "health_conditions": request.health_conditions,
                "activity_level": request.activity_level
            },

            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },

            "air_quality": air_quality,

            "aqi_classification": aqi_info,

            "personalized_risk": personalized_risk,

            "advisory": llm_advisory.model_dump(),

            "evidence": [
                {
                    "source": document.metadata.get("source"),
                    "category": document.metadata.get("category"),
                    "topic": document.metadata.get("topic"),
                    "aqi_min": document.metadata.get("aqi_min"),
                    "aqi_max": document.metadata.get("aqi_max")
                }
                for document in rag_result["documents"]
            ]
        }

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=str(e)
        )