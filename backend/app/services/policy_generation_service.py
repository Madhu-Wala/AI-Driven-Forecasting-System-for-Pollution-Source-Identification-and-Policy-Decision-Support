import json
import re
from typing import Any

from app.services.advisory_llm_service import get_advisory_llm

from app.schemas.policy_response import (
    PolicyGenerationResponse,
    StationSummary,
    SourceAssessment,
    ExpectedImpact,
    SimulationInput,
    PolicyEvidence,
)


def _safe_float(value):
    """Convert a value to float when possible."""

    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def _get_station_summary(station_data: dict) -> StationSummary:
    """Create a station summary from actual backend data."""

    return StationSummary(
        station_id=str(station_data.get("station_id", "Unknown")),
        station_name=str(station_data.get("station_name", "Unknown")),
        aqi=_safe_float(station_data.get("aqi")),
        aqi_category=station_data.get("aqi_category"),
    )


def _get_source_assessment(station_data: dict) -> list:
    """
    Convert existing source-identification scores into
    dashboard-friendly source assessment records.

    The original scores are preserved. They are not treated
    as emission contribution percentages.
    """

    source_scores = station_data.get("category_scores", {})

    if not isinstance(source_scores, dict):
        return []

    assessments = []

    for source_name, source_score in source_scores.items():

        score = _safe_float(source_score)

        if score is None:
            signal = "unknown"
            interpretation = "A valid numerical source signal is unavailable."

        elif score > 0:
            signal = "positive"
            interpretation = (
                "The pollutant indicators associated with this category "
                "are elevated relative to the historical baseline."
            )

        elif score < 0:
            signal = "negative"
            interpretation = (
                "The pollutant indicators associated with this category "
                "are below the historical baseline."
            )

        else:
            signal = "neutral"
            interpretation = (
                "The pollutant indicators associated with this category "
                "are approximately at the historical baseline."
            )

        assessments.append(
            SourceAssessment(
                source=str(source_name),
                score=score,
                signal=signal,
                interpretation=interpretation,
            )
        )

    return assessments


def _prepare_evidence(evidence: list) -> list:
    """Assign stable evidence IDs for the current LLM request."""

    prepared = []

    for index, item in enumerate(evidence, start=1):

        prepared.append({
            "evidence_id": f"EV_{index:03d}",
            "source": str(item.get("source", "Unknown")),
            "category": str(item.get("category", "Unknown")),
            "file_name": str(item.get("file_name", "Unknown")),
            "content": str(item.get("evidence", "")),
        })

    return prepared


def _extract_json(response_text: str) -> dict:
    """Extract JSON from the LLM response."""

    cleaned = response_text.strip()

    # Handle JSON wrapped in Markdown code fences.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return json.loads(cleaned)


def _build_policy_prompt(
    station_data: dict,
    source_assessment: list,
    evidence: list,
) -> str:

    station_information = {
        "station_id": station_data.get("station_id"),
        "station_name": station_data.get("station_name"),
        "aqi": station_data.get("aqi"),
        "aqi_category": station_data.get("aqi_category"),
        "category_scores": station_data.get("category_scores", {}),
        "pollutant_anomalies": station_data.get(
            "pollutant_anomalies", {}
        ),
    }

    return f"""
You are an air-pollution policy decision-support assistant
for a Mumbai air-quality monitoring dashboard.

Your task is to generate practical policy recommendations
using the supplied station data and Authority RAG evidence.

STATION DATA:
{json.dumps(station_information, indent=2, default=str)}

SOURCE ASSESSMENT:
{json.dumps(source_assessment, indent=2, default=str)}

RETRIEVED AUTHORITY EVIDENCE:
{json.dumps(evidence, indent=2, default=str)}

INSTRUCTIONS:

1. Interpret source scores as heuristic pollutant signals.
   They are NOT confirmed source contributions or percentages.

2. Do not claim that a particular industry, road, construction
   site or facility is responsible unless the supplied evidence
   explicitly establishes that fact.

3. Recommend interventions only when they are supported by
   the supplied Authority RAG evidence and relevant to the
   station's source signals.

4. Consider applicable Mumbai policies, national policies,
   mitigation guidance, NAAQS and GRAP documents where relevant.

5. Identify a responsible authority only when the evidence
   supports that responsibility. Otherwise use:
   "Relevant authority to be verified".

6. Do not invent:
   - AQI reduction values
   - PM2.5 or PM10 reduction percentages
   - Financial costs
   - Implementation timelines
   - Emission reduction percentages
   - Numerical simulation coefficients

7. For expected impact, describe the likely direction or
   purpose of the intervention qualitatively. Mark quantitative
   estimates as unavailable unless an actual validated
   quantitative estimate is present in the supplied evidence.

8. Every recommendation must cite one or more evidence IDs
   from the supplied evidence. Never invent evidence IDs.

9. If the evidence is insufficient for a recommendation,
   do not generate that recommendation.

10. Keep recommendations specific, actionable and concise.

Return ONLY valid JSON. Do not include Markdown fences,
introductory text or explanations outside the JSON.

Use exactly this structure:

{{
  "recommendations": [
    {{
      "recommendation_id": "REC_001",
      "title": "Short intervention title",
      "intervention": "Specific policy intervention",
      "rationale": "Why this intervention is relevant to the station",
      "priority": "high",
      "responsible_authority": "Authority supported by evidence",
      "implementation_conditions": [
        "Condition or verification requirement"
      ],
      "expected_impact": {{
        "description": "Qualitative expected outcome",
        "quantitative_estimate_available": false,
        "quantitative_estimate": null,
        "reason": "No validated numerical impact estimate was supplied"
      }},
      "evidence_ids": ["EV_001"]
    }}
  ],
  "limitations": [
    "Relevant limitation or uncertainty"
  ]
}}

The priority must be high, medium or low.
Return an empty recommendations list if the evidence
does not support a defensible intervention.
"""


def _build_simulation_inputs(recommendations: list) -> list:
    """
    Create simulation-ready intervention descriptors.

    No quantitative impact coefficients are assumed.
    """

    simulation_inputs = []

    for recommendation in recommendations:

        intervention_text = (
            recommendation.intervention.lower()
        )

        if "road" in intervention_text or "dust" in intervention_text:
            intervention_type = "road_dust_control"

        elif "construction" in intervention_text:
            intervention_type = "construction_dust_control"

        elif "traffic" in intervention_text or "vehicle" in intervention_text:
            intervention_type = "traffic_emission_control"

        elif "industrial" in intervention_text or "industry" in intervention_text:
            intervention_type = "industrial_emission_control"

        else:
            intervention_type = "general_air_quality_intervention"

        simulation_inputs.append(
            SimulationInput(
                recommendation_id=recommendation.recommendation_id,
                intervention_type=intervention_type,
                selected=False,
                parameters={},
                quantitative_effect_available=False,
                limitation=(
                    "Validated quantitative intervention coefficients "
                    "are not currently available."
                ),
            )
        )

    return simulation_inputs


def generate_policy_recommendations(
    station_data: dict,
    retrieved_evidence: list,
) -> dict:
    """
    Generate source-aware policy recommendations using
    Groq LLM and Authority RAG evidence.

    Returns a validated JSON-compatible dictionary.
    """

    if not station_data:
        raise ValueError("Station data is required.")

    if not retrieved_evidence:
        raise ValueError(
            "Authority RAG evidence is required for policy generation."
        )

    station_summary = _get_station_summary(station_data)

    source_assessment = _get_source_assessment(station_data)

    prepared_evidence = _prepare_evidence(
        retrieved_evidence
    )

    prompt = _build_policy_prompt(
        station_data=station_data,
        source_assessment=source_assessment,
        evidence=prepared_evidence,
    )

    llm = get_advisory_llm()

    response = llm.invoke(prompt)

    response_text = response.content

    if isinstance(response_text, list):
        response_text = "".join(
            str(part.get("text", ""))
            if isinstance(part, dict)
            else str(part)
            for part in response_text
        )

    llm_data = _extract_json(str(response_text))

    # Validate the generated recommendations.
    recommendations_data = llm_data.get("recommendations", [])

    valid_evidence_ids = {
        item["evidence_id"]
        for item in prepared_evidence
    }

    # Remove recommendations that cite nonexistent evidence.
    validated_recommendations = []

    for item in recommendations_data:

        cited_ids = item.get("evidence_ids", [])

        if not cited_ids:
            continue

        if not set(cited_ids).issubset(valid_evidence_ids):
            continue

        validated_recommendations.append(item)

    # Build typed recommendation objects.
    from app.schemas.policy_response import PolicyRecommendation

    recommendations = [
        PolicyRecommendation.model_validate(item)
        for item in validated_recommendations
    ]

    # No validated quantitative intervention model is connected yet.
    # Therefore, do not pass LLM-generated numerical estimates
    # to the simulation layer.
    for recommendation in recommendations:
        recommendation.expected_impact.quantitative_estimate_available = False
        recommendation.expected_impact.quantitative_estimate = None

        if not recommendation.expected_impact.reason:
            recommendation.expected_impact.reason = (
                "Validated quantitative intervention coefficients "
                "are not currently available."
            )

    # Keep evidence metadata; full evidence text is not needed
    # in the final dashboard payload.
    selected_evidence = [
        PolicyEvidence(
            evidence_id=item["evidence_id"],
            source=item["source"],
            category=item["category"],
            file_name=item["file_name"],
        )
        for item in prepared_evidence
        if any(
            item["evidence_id"] in recommendation.evidence_ids
            for recommendation in recommendations
        )
    ]

    simulation_inputs = _build_simulation_inputs(
        recommendations
    )

    limitations = llm_data.get("limitations", [])

    # Add a consistent explanation of the heuristic source scores.
    limitations.append(
        "Source-identification scores are heuristic pollutant signals, "
        "not confirmed emission contribution percentages."
    )

    final_response = PolicyGenerationResponse(
        station_summary=station_summary,
        source_assessment=source_assessment,
        recommendations=recommendations,
        simulation_inputs=simulation_inputs,
        evidence=selected_evidence,
        limitations=limitations,
    )

    return final_response.model_dump()