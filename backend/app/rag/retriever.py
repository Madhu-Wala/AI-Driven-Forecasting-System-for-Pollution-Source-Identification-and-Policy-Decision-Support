from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


PROJECT_ROOT = Path(__file__).resolve().parents[3]

VECTOR_STORE_PATH = (
    PROJECT_ROOT
    / "Knowledge_Base_RAG"
    / "citizen"
    / "vector_store"
)


def get_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )


def retrieve_aqi_relevant_documents(query: str, aqi: float, k: int = 5):
    vector_store = get_vector_store()

    candidates = vector_store.similarity_search(
        query,
        k=max(k * 5, 20),
    )

    relevant_documents = []

    for document in candidates:
        aqi_min = document.metadata.get("aqi_min")
        aqi_max = document.metadata.get("aqi_max")

        # General evidence
        if aqi_min is None or aqi_max is None:
            relevant_documents.append(document)
            continue

        # AQI-specific evidence
        if aqi_min <= aqi <= aqi_max:
            relevant_documents.append(document)

    return relevant_documents


def get_citizen_retriever(k: int = 5):
    """
    Backward-compatible generic retriever.
    """

    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_kwargs={
            "k": k
        }
    )