from typing import List

from langchain_core.documents import Document


def filter_advisory_evidence(
    documents: List[Document],
    aqi: float
) -> List[Document]:
    """
    Keep retrieved evidence that is relevant to the current AQI.

    This version does not discard an entire document merely because
    it contains recommendations for higher AQI levels.
    """

    filtered_documents = []

    for document in documents:

        content = document.page_content.lower()

        # Clearly higher-AQI-specific sections
        high_aqi_300_terms = [
            "aqi > 300",
            "aqi >300",
            "aqi 300+",
            "aqi above 300",
            "aqi crosses 300",
            "aqi is above 300",
        ]

        high_aqi_200_terms = [
            "aqi 200–300",
            "aqi 200-300",
            "aqi 201–300",
            "aqi 201-300",
        ]

        # If the entire chunk is clearly about AQI > 300,
        # do not use it for lower AQI values.
        if aqi <= 300 and any(
            term in content for term in high_aqi_300_terms
        ):

            # Keep the document if it also contains a
            # lower-AQI range such as 101–200.
            lower_aqi_terms = [
                "aqi 101–200",
                "aqi 101-200",
                "aqi 100–200",
                "aqi 100-200",
                "moderate",
            ]

            if not any(
                term in content
                for term in lower_aqi_terms
            ):
                continue

        # If AQI is below 200, discard chunks whose
        # content is specifically about 200–300.
        if aqi < 200:

            if any(
                term in content
                for term in high_aqi_200_terms
            ):

                lower_aqi_terms = [
                    "aqi 101–200",
                    "aqi 101-200",
                    "aqi 100–200",
                    "aqi 100-200",
                    "moderate",
                ]

                if not any(
                    term in content
                    for term in lower_aqi_terms
                ):
                    continue

        filtered_documents.append(document)

    return filtered_documents