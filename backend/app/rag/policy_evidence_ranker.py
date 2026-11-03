def calculate_policy_evidence_score(document, source_signals: dict):

    score = 0

    category = str(
        document.metadata.get("category", "")
    ).lower()

    content = document.page_content.lower()

    source_keywords = {
        "traffic": [
            "traffic", "transport", "vehicle", "emission", "road"
        ],
        "industry": [
            "industrial", "industry", "factory", "emission", "so2"
        ],
        "road_dust_construction": [
            "road dust", "construction", "dust",
            "demolition", "debris"
        ]
    }

    for source_name, source_score in source_signals.items():

        try:
            is_positive = float(source_score) > 0
        except (TypeError, ValueError):
            is_positive = False

        if not is_positive:
            continue

        keywords = source_keywords.get(source_name, [])

        if any(keyword in content for keyword in keywords):
            score += 3

        if source_name in category:
            score += 2

    if category in {
        "mitigation",
        "policy_frameworks",
        "grap",
        "standards"
    }:
        score += 1

    return score


def rank_policy_evidence(documents, source_signals: dict, k: int = 5):

    scored_documents = []

    for document in documents:

        score = calculate_policy_evidence_score(
            document,
            source_signals
        )

        scored_documents.append((score, document))

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        document
        for score, document in scored_documents[:k]
    ]