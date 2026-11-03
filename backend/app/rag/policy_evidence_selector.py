def select_policy_evidence(documents):

    selected_evidence = []

    for document in documents:

        selected_evidence.append({
            "source": document.metadata.get(
                "source", "Unknown source"
            ),
            "category": document.metadata.get(
                "category", "Unknown"
            ),
            "file_name": document.metadata.get(
                "file_name", "Unknown"
            ),
            "evidence": document.page_content.strip()
        })

    return selected_evidence