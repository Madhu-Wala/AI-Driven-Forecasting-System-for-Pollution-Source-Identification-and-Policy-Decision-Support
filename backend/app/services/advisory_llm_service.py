import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.models.advisory_response import AdvisoryResponse

load_dotenv()

from app.models.advisory_response import AdvisoryResponse


def get_advisory_llm():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured"
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=3000,
        api_key=api_key,
    )

def format_evidence(documents):

    evidence_blocks = []

    for index, document in enumerate(documents, start=1):

        source = document.metadata.get(
            "source",
            "Unknown source"
        )

        aqi_min = document.metadata.get("aqi_min")
        aqi_max = document.metadata.get("aqi_max")
        topic = document.metadata.get(
            "topic",
            "general"
        )

        evidence_blocks.append(
            f"""
Evidence {index}
Source: {source}
AQI range: {aqi_min}–{aqi_max}
Topic: {topic}

{document.page_content}
"""
        )

    return "\n".join(evidence_blocks)

def build_advisory_prompt(
    age_group,
    health_conditions,
    activity_level,
    aqi,
    aqi_category,
    personalized_risk,
    evidence,
):

    conditions = (
        ", ".join(health_conditions)
        if health_conditions
        else "None"
    )

    return f"""
You are an air-pollution health advisory assistant.

Your task is to generate a personalized CITIZEN AIR-POLLUTION
ADVISORY.

This system does NOT diagnose diseases, prescribe medicines,
or replace a doctor.

Use ONLY the supplied structured profile, deterministic risk
assessment, and retrieved knowledge-base evidence.

Do NOT invent medical facts.

Do NOT change or reinterpret the supplied AQI category.

Do NOT create a diagnosis.

Do NOT prescribe or change medication.

If medication is mentioned in the evidence, only advise the
citizen to follow their existing prescribed medical plan or
seek professional medical advice.

CITIZEN PROFILE
---------------
Age group: {age_group}
Health conditions: {conditions}
Activity level: {activity_level}

CURRENT AIR QUALITY
-------------------
AQI: {aqi}
AQI category: {aqi_category}

DETERMINISTIC PERSONALIZATION
-----------------------------
{personalized_risk}

RETRIEVED KNOWLEDGE-BASE EVIDENCE
----------------------------------
{evidence}

INSTRUCTIONS
------------

1. Provide a concise personalized summary.

2. Provide practical recommendations for today.

3. Base activity timing and outdoor-exposure guidance primarily
   on the supplied AQI category and deterministic activity
   recommendation.

4. Use the retrieved knowledge-base evidence to support
   additional health precautions.

5. ONLY include a recommendation if it is supported by either:
   - the deterministic personalization assessment, OR
   - the retrieved knowledge-base evidence.

6. Do NOT use your general medical knowledge to add advice.

7. Do NOT invent recommendations.

8. Do NOT recommend masks, air purifiers, medicines,
   supplements, inhalers, treatments, or medical devices
   unless the supplied evidence explicitly supports that
   recommendation for the current situation.

9. Do NOT recommend medication or changes to medication.

10. Do NOT recommend avoiding outdoor activity when the
    supplied AQI category and deterministic assessment
    indicate that outdoor activity can generally continue.

11. Do NOT recommend a specific time of day unless the
    supplied evidence explicitly provides that timing.

12. Do NOT change or reinterpret the supplied AQI category.

13. Do NOT invent AQI thresholds.

14. Warning symptoms must ONLY be included when supported
    by the retrieved evidence.

15. If there is insufficient evidence for a protective measure
    or warning sign, return an empty list instead of guessing.

16. Give additional emphasis to the citizen's stated health
    conditions, but do not invent condition-specific medical
    advice.

17. Do not mention RAG, embeddings, vector stores, prompts,
    models, or software implementation.

18. Use simple language suitable for an ordinary citizen.

19. Include the exact knowledge-base source filenames used.

20. Keep the response concise:
    - maximum 4 daily recommendations
    - maximum 3 protective measures
    - maximum 3 warning signs

21. End with a clear disclaimer that this is general health
    guidance and not medical diagnosis or treatment.

Return ONLY the requested structured response.
Keep the response concise.
Use at most 4 recommendations, 3 protective measures,
and 3 warning signs.
Do not provide explanations outside the requested fields.
"""

def generate_llm_advisory(
    age_group,
    health_conditions,
    activity_level,
    aqi,
    aqi_category,
    personalized_risk,
    documents,
):

    llm = get_advisory_llm()

    evidence = format_evidence(documents)

    prompt = build_advisory_prompt(
        age_group=age_group,
        health_conditions=health_conditions,
        activity_level=activity_level,
        aqi=aqi,
        aqi_category=aqi_category,
        personalized_risk=personalized_risk,
        evidence=evidence,
    )

    structured_llm = llm.with_structured_output(
        AdvisoryResponse,
        method="json_schema",
        strict=True,
    )

    response = structured_llm.invoke(prompt)

    return response