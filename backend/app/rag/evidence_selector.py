from typing import List, Dict

from langchain_core.documents import Document


def _get_aqi_range(aqi: float) -> str:
    """Return the applicable CPCB AQI range."""

    if aqi <= 50:
        return "0-50"
    elif aqi <= 100:
        return "51-100"
    elif aqi <= 200:
        return "101-200"
    elif aqi <= 300:
        return "201-300"
    elif aqi <= 400:
        return "301-400"
    else:
        return "401-500"


def _line_contains_aqi_range(line: str) -> bool:
    """Check whether a line contains an AQI-specific range."""

    text = line.lower()

    ranges = [
        "aqi 0–50",
        "aqi 0-50",
        "aqi 51–100",
        "aqi 51-100",
        "aqi 100–200",
        "aqi 100-200",
        "aqi 101–200",
        "aqi 101-200",
        "aqi 200–300",
        "aqi 200-300",
        "aqi 201–300",
        "aqi 201-300",
        "aqi 300+",
        "aqi 300 +",
        "aqi 301–400",
        "aqi 301-400",
        "aqi 401–500",
        "aqi 401-500",
    ]

    return any(term in text for term in ranges)


def _is_current_aqi_line(
    line: str,
    aqi: float
) -> bool:
    """Return True if an AQI-specific line applies to the current AQI."""

    text = line.lower()
    current_range = _get_aqi_range(aqi)

    if current_range == "0-50":
        return (
            "aqi 0–50" in text
            or "aqi 0-50" in text
        )

    if current_range == "51-100":
        return (
            "aqi 51–100" in text
            or "aqi 51-100" in text
        )

    if current_range == "101-200":
        return (
            "aqi 101–200" in text
            or "aqi 101-200" in text
            or "aqi 100–200" in text
            or "aqi 100-200" in text
            or "moderate (101–200)" in text
            or "moderate (101-200)" in text
        )

    if current_range == "201-300":
        return (
            "aqi 201–300" in text
            or "aqi 201-300" in text
            or "aqi 200–300" in text
            or "aqi 200-300" in text
        )

    if current_range == "301-400":
        return (
            "aqi 301–400" in text
            or "aqi 301-400" in text
            or "aqi 300+" in text
            or "aqi 300 +" in text
        )

    if current_range == "401-500":
        return (
            "aqi 401–500" in text
            or "aqi 401-500" in text
        )

    return False


def _is_higher_aqi_line(
    line: str,
    aqi: float
) -> bool:
    """Identify AQI-specific guidance for a higher range."""

    text = line.lower()

    higher_ranges = []

    if aqi <= 50:
        higher_ranges = [
            "aqi 51–100",
            "aqi 51-100",
            "aqi 100–200",
            "aqi 100-200",
            "aqi 101–200",
            "aqi 101-200",
            "aqi 200–300",
            "aqi 200-300",
            "aqi 201–300",
            "aqi 201-300",
            "aqi 300+",
        ]

    elif aqi <= 100:
        higher_ranges = [
            "aqi 100–200",
            "aqi 100-200",
            "aqi 101–200",
            "aqi 101-200",
            "aqi 200–300",
            "aqi 200-300",
            "aqi 201–300",
            "aqi 201-300",
            "aqi 300+",
        ]

    elif aqi <= 200:
        higher_ranges = [
            "aqi 200–300",
            "aqi 200-300",
            "aqi 201–300",
            "aqi 201-300",
            "aqi 300+",
            "aqi 300 +",
            "aqi > 300",
            "aqi >300",
            "aqi above 300",
        ]

    elif aqi <= 300:
        higher_ranges = [
            "aqi 300+",
            "aqi 300 +",
            "aqi > 300",
            "aqi >300",
            "aqi above 300",
        ]

    return any(term in text for term in higher_ranges)


def _is_profile_relevant(
    line: str,
    health_conditions: List[str],
    activity_level: str
) -> bool:
    """Check whether general evidence matches the user profile."""

    text = line.lower()

    conditions = {
        condition.strip().lower()
        for condition in health_conditions
    }

    respiratory_conditions = {
        "asthma",
        "copd / chronic lung condition",
        "other respiratory condition"
    }

    cardiovascular_conditions = {
        "heart / cardiovascular condition"
    }

    if conditions.intersection(respiratory_conditions):

        if any(
            term in text
            for term in [
                "asthma",
                "respiratory",
                "breathing",
                "wheezing",
                "shortness of breath",
                "cough",
            ]
        ):
            return True

    if conditions.intersection(cardiovascular_conditions):

        if any(
            term in text
            for term in [
                "heart",
                "cardiac",
                "cardiovascular",
            ]
        ):
            return True

    if activity_level in {
        "Heavy Activity",
        "Moderate Activity"
    }:

        if any(
            term in text
            for term in [
                "outdoor activity",
                "outdoor exposure",
                "physical activity",
                "exercise",
                "prolonged exposure",
            ]
        ):
            return True

    return False


def select_advisory_evidence(
    documents: List[Document],
    aqi: float,
    age_group: str,
    health_conditions: List[str],
    activity_level: str
) -> List[Dict]:
    """
    Select evidence applicable to the current AQI and
    citizen profile.
    """

    selected_evidence = []

    for document in documents:

        selected_lines = []

        for line in document.page_content.splitlines():

            line = line.strip()

            if not line:
                continue

            # ------------------------------------------------
            # 1. AQI-specific line
            # ------------------------------------------------

            if _line_contains_aqi_range(line):

                if _is_current_aqi_line(line, aqi):

                    if line not in selected_lines:
                        selected_lines.append(line)

                continue

            # ------------------------------------------------
            # 2. General guidance
            # ------------------------------------------------

            if _is_higher_aqi_line(line, aqi):
                continue

            # Keep general monitoring guidance.
            if any(
                term in line.lower()
                for term in [
                    "monitor aqi",
                    "monitor local aqi",
                    "check aqi",
                    "stay informed",
                ]
            ):

                if line not in selected_lines:
                    selected_lines.append(line)

                continue

            # Keep profile-specific guidance.
            if _is_profile_relevant(
                line=line,
                health_conditions=health_conditions,
                activity_level=activity_level
            ):

                if line not in selected_lines:
                    selected_lines.append(line)

        if selected_lines:

            selected_evidence.append(
                {
                    "source": document.metadata.get(
                        "source",
                        "Unknown source"
                    ),
                    "category": document.metadata.get(
                        "category",
                        "Unknown"
                    ),
                    "evidence": selected_lines
                }
            )

    return selected_evidence