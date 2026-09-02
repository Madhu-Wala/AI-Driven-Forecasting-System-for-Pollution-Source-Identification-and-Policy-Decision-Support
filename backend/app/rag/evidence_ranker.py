def _normalize(value: str) -> str:
    return value.lower().strip() if value else ""


def calculate_evidence_score(
    document,
    aqi: float,
    health_conditions: list[str],
    activity_level: str,
) -> int:
    """
    Rank retrieved evidence based on:
    1. AQI applicability
    2. Health-condition relevance
    3. Activity relevance
    4. Topic relevance

    This is a retrieval-ranking heuristic, not a medical risk score.
    """

    score = 0

    metadata = document.metadata

    aqi_min = metadata.get("aqi_min")
    aqi_max = metadata.get("aqi_max")
    topic = _normalize(metadata.get("topic", ""))

    content = _normalize(document.page_content)

    # ---------------------------------------------------------
    # 1. AQI relevance
    # ---------------------------------------------------------

    if aqi_min is not None and aqi_max is not None:
        if aqi_min <= aqi <= aqi_max:
            score += 5

            # Give a small bonus to narrower/more precise ranges.
            range_width = aqi_max - aqi_min

            if range_width <= 50:
                score += 2
            elif range_width <= 100:
                score += 1

    else:
        # General evidence is useful, but should rank below
        # evidence explicitly tied to the current AQI.
        score += 1

    # ---------------------------------------------------------
    # 2. Health-condition relevance
    # ---------------------------------------------------------

    conditions = [_normalize(c) for c in health_conditions]

    respiratory_conditions = {
        "asthma",
        "copd / chronic lung condition",
        "other respiratory condition",
    }

    cardiovascular_conditions = {
        "heart / cardiovascular condition",
    }

    for condition in conditions:

        if condition in respiratory_conditions:
            if topic == "respiratory":
                score += 4

            if any(
                keyword in content
                for keyword in [
                    "asthma",
                    "respiratory",
                    "lung",
                    "breathing",
                    "wheezing",
                    "cough",
                ]
            ):
                score += 2

        elif condition in cardiovascular_conditions:
            if topic in {"respiratory", "general"}:
                score += 2

            if any(
                keyword in content
                for keyword in [
                    "cardiac",
                    "cardiovascular",
                    "heart",
                ]
            ):
                score += 3

        elif condition == "diabetes":
            if "diabetes" in content:
                score += 4

        elif condition == "allergies / sinusitis":
            if any(
                keyword in content
                for keyword in [
                    "allerg",
                    "sinus",
                    "nose",
                    "throat",
                    "irritation",
                ]
            ):
                score += 4

        elif condition == "pregnancy":
            if any(
                keyword in content
                for keyword in [
                    "pregnant",
                    "pregnancy",
                    "fetus",
                    "birth",
                ]
            ):
                score += 4

        elif condition == "other / not listed":
            if topic in {"respiratory", "general"}:
                score += 1

    # ---------------------------------------------------------
    # 3. Activity relevance
    # ---------------------------------------------------------

    activity = _normalize(activity_level)

    if activity == "heavy activity":
        if topic == "activity":
            score += 4

        if any(
            keyword in content
            for keyword in [
                "heavy exercise",
                "strenuous exercise",
                "strenuous outdoor",
                "outdoor workout",
                "running",
                "cycling",
                "jogging",
                "physical exertion",
            ]
        ):
            score += 3

    elif activity == "moderate activity":
        if topic == "activity":
            score += 4

        if any(
            keyword in content
            for keyword in [
                "exercise",
                "physical activity",
                "outdoor activity",
            ]
        ):
            score += 2

    elif activity == "light activity":
        if topic == "activity":
            score += 3

        if any(
            keyword in content
            for keyword in [
                "walking",
                "light exercise",
                "light activity",
            ]
        ):
            score += 2

    # ---------------------------------------------------------
    # 4. Protective measures
    # ---------------------------------------------------------

    if topic == "protective_measures":
        score += 2

    if any(
        keyword in content
        for keyword in [
            "n95",
            "n99",
            "air purifier",
            "seal windows",
            "stay indoors",
        ]
    ):
        score += 1

    # ---------------------------------------------------------
    # 5. Warning symptoms
    # ---------------------------------------------------------

    if topic == "warning_signs":
        score += 2

    if any(
        keyword in content
        for keyword in [
            "breathing difficulty",
            "shortness of breath",
            "wheezing",
            "chest tightness",
            "persistent coughing",
        ]
    ):
        score += 1

    return score


def rank_evidence(
    documents,
    aqi: float,
    health_conditions: list[str],
    activity_level: str,
    k: int = 5,
):
    """
    Score and rank already AQI-filtered documents.
    """

    scored_documents = []

    for document in documents:
        score = calculate_evidence_score(
            document=document,
            aqi=aqi,
            health_conditions=health_conditions,
            activity_level=activity_level,
        )

        scored_documents.append((score, document))

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        document
        for score, document in scored_documents[:k]
    ]