from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


PROJECT_ROOT = Path(__file__).resolve().parents[3]

AUTHORITY_VECTOR_STORE_PATH = (
    PROJECT_ROOT
    / "Knowledge_Base_RAG"
    / "authority"
    / "vector_store"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_authority_vector_store():

    index_file = AUTHORITY_VECTOR_STORE_PATH / "index.faiss"
    metadata_file = AUTHORITY_VECTOR_STORE_PATH / "index.pkl"

    if not index_file.exists() or not metadata_file.exists():
        raise RuntimeError(
            "Authority vector store not found. "
            "Build it using the Authority RAG build endpoint."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    return FAISS.load_local(
        str(AUTHORITY_VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )


def retrieve_authority_documents(query: str, k: int = 5):

    vector_store = get_authority_vector_store()

    return vector_store.similarity_search(
        query,
        k=k
    )