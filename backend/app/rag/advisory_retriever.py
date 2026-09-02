from app.rag.retriever import retrieve_aqi_relevant_documents
from app.rag.context_builder import build_advisory_query
from app.rag.evidence_ranker import rank_evidence


def retrieve_advisory_evidence(
    age_group,
    health_conditions,
    activity_level,
    aqi,
    aqi_category,
    k=5,
):
    query = build_advisory_query(
        age_group=age_group,
        health_conditions=health_conditions,
        activity_level=activity_level,
        aqi=aqi,
        aqi_category=aqi_category,
    )

    # First filter by AQI applicability.
    documents = retrieve_aqi_relevant_documents(
        query=query,
        aqi=aqi,
        k=k,
    )

    # Then rank the applicable evidence according to
    # the citizen's health conditions and activity.
    ranked_documents = rank_evidence(
        documents=documents,
        aqi=aqi,
        health_conditions=health_conditions,
        activity_level=activity_level,
        k=k,
    )

    return {
        "query": query,
        "documents": ranked_documents,
    }