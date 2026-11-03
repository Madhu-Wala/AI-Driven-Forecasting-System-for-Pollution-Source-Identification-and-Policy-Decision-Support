from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.rag.authority_vector_store import (
    build_authority_vector_store,
    AUTHORITY_VECTOR_STORE_PATH
)

from app.rag.authority_retriever import (
    retrieve_authority_documents
)

from app.rag.policy_context_builder import (
    build_policy_query
)

from app.rag.policy_evidence_ranker import (
    rank_policy_evidence
)

from app.rag.policy_evidence_selector import (
    select_policy_evidence
)

from app.services.source_identification_service import (
    get_source_identification_by_station
)

from app.services.policy_generation_service import (
    generate_policy_recommendations
)


router = APIRouter(
    prefix="/api/policy/rag",
    tags=["Policy Authority RAG"]
)


class PolicyRetrievalRequest(BaseModel):
    query: str = Field(min_length=3)
    k: int = Field(default=5, ge=1, le=20)


@router.get("/status")
def get_authority_rag_status():

    index_file = AUTHORITY_VECTOR_STORE_PATH / "index.faiss"
    metadata_file = AUTHORITY_VECTOR_STORE_PATH / "index.pkl"

    available = index_file.exists() and metadata_file.exists()

    return {
        "available": available,
        "vector_store_path": str(AUTHORITY_VECTOR_STORE_PATH),
        "message": (
            "Authority vector store is available."
            if available
            else "Authority vector store has not been built yet."
        )
    }


@router.post("/build")
def build_authority_rag():

    try:
        build_authority_vector_store()

        return {
            "success": True,
            "message": "Authority vector store built successfully."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to build Authority RAG: {str(e)}"
        )


@router.post("/retrieve")
def retrieve_policy_evidence(
    request: PolicyRetrievalRequest
):

    try:
        documents = retrieve_authority_documents(
            query=request.query,
            k=request.k
        )

        evidence = select_policy_evidence(documents)

        return {
            "query": request.query,
            "total_results": len(evidence),
            "evidence": evidence
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Policy evidence retrieval failed: {str(e)}"
        )


@router.post("/station/{station_id}")
def retrieve_station_policy_evidence(
    station_id: str,
    k: int = Query(default=5, ge=1, le=20)
):

    try:
        station_data = get_source_identification_by_station(
            station_id
        )

        if not station_data:
            raise HTTPException(
                status_code=404,
                detail="Source-identification data not found for this station."
            )

        query = build_policy_query(station_data)

        documents = retrieve_authority_documents(
            query=query,
            k=max(k * 3, 15)
        )

        source_signals = station_data.get(
            "category_scores", {}
        )

        ranked_documents = rank_policy_evidence(
            documents=documents,
            source_signals=source_signals,
            k=k
        )

        evidence = select_policy_evidence(
            ranked_documents
        )

        return {
            "station_id": station_id,
            "station_data": station_data,
            "query": query,
            "total_results": len(evidence),
            "evidence": evidence
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Station policy retrieval failed: {str(e)}"
        )


@router.post("/station/{station_id}/recommendations")
def generate_station_policy_recommendations(
    station_id: str,
    k: int = Query(default=5, ge=1, le=20)
):
    """
    Generate source-aware policy recommendations for a station
    using source-identification results, Authority RAG and Groq.
    """

    try:
        # STEP 1: Get station source-identification data.
        station_data = get_source_identification_by_station(
            station_id
        )

        if not station_data:
            raise HTTPException(
                status_code=404,
                detail="Source-identification data not found for this station."
            )

        # STEP 2: Build a query using station information.
        query = build_policy_query(station_data)

        # STEP 3: Retrieve more candidates than the final K.
        retrieved_documents = retrieve_authority_documents(
            query=query,
            k=max(k * 3, 15)
        )

        # STEP 4: Rank documents according to source signals.
        source_signals = station_data.get(
            "category_scores", {}
        )

        ranked_documents = rank_policy_evidence(
            documents=retrieved_documents,
            source_signals=source_signals,
            k=k
        )

        # STEP 5: Convert retrieved documents into evidence records.
        evidence = select_policy_evidence(
            ranked_documents
        )

        if not evidence:
            raise HTTPException(
                status_code=404,
                detail="No relevant Authority RAG evidence was retrieved."
            )

        # STEP 6: Pass station data and evidence to the LLM.
        policy_response = generate_policy_recommendations(
            station_data=station_data,
            retrieved_evidence=evidence
        )

        # STEP 7: Return structured JSON for the dashboard.
        return {
            "success": True,
            "station_id": station_id,
            "policy_response": policy_response
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Policy recommendation generation failed: {str(e)}"
        )