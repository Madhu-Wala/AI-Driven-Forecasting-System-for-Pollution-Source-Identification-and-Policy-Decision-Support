from pathlib import Path
from langchain_core.documents import Document


# Project root:
# backend/app/rag/document_loader.py
#       ↓
# project root is three levels above this file
PROJECT_ROOT = Path(__file__).resolve().parents[3]

CITIZEN_KB_PATH = PROJECT_ROOT / "Knowledge_Base_RAG" / "citizen"


def load_citizen_documents():
    """
    Load only citizen-side Markdown documents from the
    Knowledge_Base_RAG directory.
    """

    documents = []

    for file_path in CITIZEN_KB_PATH.rglob("*.md"):

        # Skip README files
        if file_path.name.lower() == "readme.md":
            continue

        text = file_path.read_text(
            encoding="utf-8"
        )

        relative_path = file_path.relative_to(
            CITIZEN_KB_PATH
        )

        category = relative_path.parts[0]

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(relative_path),
                    "category": category,
                    "file_name": file_path.name
                }
            )
        )

    return documents