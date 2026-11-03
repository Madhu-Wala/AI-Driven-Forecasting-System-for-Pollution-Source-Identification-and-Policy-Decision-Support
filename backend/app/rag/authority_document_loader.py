from pathlib import Path
from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUTHORITY_KB_PATH = PROJECT_ROOT / "Knowledge_Base_RAG" / "authority"


def load_authority_documents():
    documents = []

    for file_path in AUTHORITY_KB_PATH.rglob("*.md"):

        if file_path.name.lower() == "readme.md":
            continue

        if "vector_store" in file_path.parts:
            continue

        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        relative_path = file_path.relative_to(AUTHORITY_KB_PATH)

        category = (
            relative_path.parts[0]
            if len(relative_path.parts) > 1
            else "general"
        )

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