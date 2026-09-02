from pathlib import Path
import re

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from app.rag.document_loader import load_citizen_documents


PROJECT_ROOT = Path(__file__).resolve().parents[3]

VECTOR_STORE_PATH = (
    PROJECT_ROOT
    / "Knowledge_Base_RAG"
    / "citizen"
    / "vector_store"
)


def detect_aqi_range(text: str):
    """
    Detect an AQI range from a line of text.

    Supports the AQI formats actually present in the
    citizen knowledge base.
    """

    normalized = text.lower().strip()

    # Specific ranges first
    patterns = [
        (r"aqi\s*0[–-]50", 0, 50),
        (r"aqi\s*51[–-]100", 51, 100),

        (r"aqi\s*101[–-]200", 101, 200),
        (r"aqi\s*100[–-]200", 100, 200),

        (r"aqi\s*151[–-]200", 151, 200),

        (r"aqi\s*201[–-]300", 201, 300),
        (r"aqi\s*200[–-]300", 200, 300),

        (r"aqi\s*301[–-]400", 301, 400),
        (r"aqi\s*401[–-]500", 401, 500),

        (r"aqi\s*300\s*\+", 300, 500),
        (r"aqi\s*>\s*300", 301, 500),
        (r"aqi\s*above\s*300", 301, 500),
        (r"above\s*300", 301, 500),

        # Bare ranges used inside Markdown tables
        (r"\|\s*0[–-]50\s*\|", 0, 50),
        (r"\|\s*51[–-]100\s*\|", 51, 100),
        (r"\|\s*101[–-]200\s*\|", 101, 200),
        (r"\|\s*100[–-]200\s*\|", 100, 200),
        (r"\|\s*151[–-]200\s*\|", 151, 200),
        (r"\|\s*201[–-]300\s*\|", 201, 300),
        (r"\|\s*200[–-]300\s*\|", 200, 300),
        (r"\|\s*301[–-]400\s*\|", 301, 400),
        (r"\|\s*401[–-]500\s*\|", 401, 500),
        (r"\|\s*300\+\s*\|", 300, 500),
        (r"\|\s*Above\s*300\s*\|", 301, 500),
    ]

    for pattern, minimum, maximum in patterns:

        if re.search(pattern, normalized):
            return minimum, maximum

    return None, None


def detect_topic(text: str) -> str:
    """
    Detect the broad topic represented by a chunk.
    """

    lower_text = text.lower()

    if any(
        term in lower_text
        for term in [
            "asthma",
            "copd",
            "respiratory",
            "breathing",
            "wheezing",
            "shortness of breath"
        ]
    ):
        return "respiratory"

    if any(
        term in lower_text
        for term in [
            "heart disease",
            "cardiac",
            "cardiovascular"
        ]
    ):
        return "cardiovascular"

    if any(
        term in lower_text
        for term in [
            "exercise",
            "physical activity",
            "outdoor activity",
            "outdoor exposure"
        ]
    ):
        return "activity"

    if any(
        term in lower_text
        for term in [
            "mask",
            "n95",
            "n99",
            "air purifier",
            "windows",
            "indoor air"
        ]
    ):
        return "protective_measures"

    if any(
        term in lower_text
        for term in [
            "warning signs",
            "warning symptoms",
            "symptoms"
        ]
    ):
        return "warning_signs"

    return "general"


def create_aqi_aware_chunks(documents):
    """
    Create chunks while preserving AQI-specific boundaries.

    Each AQI-specific row/section receives its own AQI metadata.
    General content receives None for AQI bounds.
    """

    chunks = []

    for document in documents:

        lines = document.page_content.splitlines()

        current_lines = []
        current_aqi_min = None
        current_aqi_max = None

        def save_current_chunk():

            nonlocal current_lines
            nonlocal current_aqi_min
            nonlocal current_aqi_max

            if not current_lines:
                return

            text = "\n".join(current_lines).strip()

            if not text:
                return

            chunks.append(
                Document(
                    page_content=text,
                    metadata={
                        **document.metadata,
                        "aqi_min": current_aqi_min,
                        "aqi_max": current_aqi_max,
                        "topic": detect_topic(text),
                    }
                )
            )

            current_lines = []
            current_aqi_min = None
            current_aqi_max = None

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            line_min, line_max = detect_aqi_range(
                stripped
            )

            # ---------------------------------------------
            # AQI-specific line
            # ---------------------------------------------

            if line_min is not None:

                # Save whatever came before it.
                save_current_chunk()

                # Start a completely new AQI-specific chunk.
                current_lines = [stripped]

                current_aqi_min = line_min
                current_aqi_max = line_max

                # A Markdown table row is already a
                # self-contained evidence unit.
                if stripped.startswith("|"):
                    save_current_chunk()

                continue

            # ---------------------------------------------
            # General line
            # ---------------------------------------------

            current_lines.append(stripped)

        # Save anything remaining.
        save_current_chunk()

    return chunks

def build_citizen_vector_store():

    documents = load_citizen_documents()

    if not documents:
        raise RuntimeError(
            "No citizen knowledge-base documents found."
        )

    chunks = create_aqi_aware_chunks(documents)

    print(
        f"Loaded {len(documents)} documents "
        f"and created {len(chunks)} AQI-aware chunks."
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    VECTOR_STORE_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_store.save_local(
        str(VECTOR_STORE_PATH)
    )

    print(
        f"Vector store saved to: {VECTOR_STORE_PATH}"
    )

    return vector_store


if __name__ == "__main__":
    build_citizen_vector_store()