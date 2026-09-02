from app.models.advisory_response import AdvisoryResponse


def validate_advisory(
    advisory: AdvisoryResponse,
    aqi: float,
    aqi_category: str,
    personalized_risk: dict,
) -> AdvisoryResponse:

    # ---------------------------------------------------------
    # 1. Keep the deterministic personalized risk
    # ---------------------------------------------------------

    advisory.risk_level = personalized_risk["personalized_risk"]

    # ---------------------------------------------------------
    # 2. Prevent outdoor activity advice from contradicting
    #    the deterministic assessment
    # ---------------------------------------------------------

    activity_recommendation = personalized_risk.get(
        "activity_recommendation",
        ""
    ).lower()

    outdoor_exposure = advisory.outdoor_exposure.lower()
    activity_timing = advisory.activity_timing.lower()

    high_pollution = aqi >= 201

    if high_pollution:
        # At Poor, Very Poor and Severe AQI,
        # the system should not encourage heavy outdoor activity.

        forbidden_phrases = [
            "safe to continue heavy",
            "continue heavy outdoor activity",
            "heavy outdoor activity is safe",
            "no restriction",
            "outdoor activity as usual",
        ]

        if any(
            phrase in outdoor_exposure
            for phrase in forbidden_phrases
        ):
            advisory.outdoor_exposure = (
                personalized_risk["activity_recommendation"]
            )

        if any(
            phrase in activity_timing
            for phrase in forbidden_phrases
        ):
            advisory.activity_timing = (
                personalized_risk["activity_recommendation"]
            )

    # ---------------------------------------------------------
    # 3. At Good AQI, don't allow unnecessarily strong
    #    pollution-exposure language
    # ---------------------------------------------------------

    if aqi <= 50:

        excessive_phrases = [
            "avoid outdoor activity",
            "avoid going outside",
            "stay indoors",
            "remain indoors",
            "do not go outside",
        ]

        if any(
            phrase in outdoor_exposure
            for phrase in excessive_phrases
        ):
            advisory.outdoor_exposure = (
                personalized_risk["activity_recommendation"]
            )

    # ---------------------------------------------------------
    # 4. Remove clearly unsupported generic recommendations
    # ---------------------------------------------------------

    filtered_recommendations = []

    for recommendation in advisory.todays_recommendations:

        text = recommendation.lower()

        # Medication / treatment advice should never be generated.
        medication_terms = [
            "take medication",
            "increase medication",
            "change medication",
            "stop medication",
            "use inhaler",
            "take inhaler",
        ]

        if any(term in text for term in medication_terms):
            continue

        filtered_recommendations.append(recommendation)

    advisory.todays_recommendations = filtered_recommendations[:4]

    # ---------------------------------------------------------
    # 5. Limit output sizes
    # ---------------------------------------------------------

    advisory.protective_measures = (
        advisory.protective_measures[:3]
    )

    advisory.warning_signs = (
        advisory.warning_signs[:3]
    )

    advisory.evidence_sources = (
        advisory.evidence_sources[:5]
    )

    # ---------------------------------------------------------
    # 6. Ensure disclaimer always exists
    # ---------------------------------------------------------

    if not advisory.disclaimer.strip():

        advisory.disclaimer = (
            "This guidance is general health information "
            "and is not a medical diagnosis or treatment."
        )

    return advisory