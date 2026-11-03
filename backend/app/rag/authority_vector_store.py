from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from app.rag.authority_document_loader import load_authority_documents


PROJECT_ROOT = Path(__file__).resolve().parents[3]

AUTHORITY_VECTOR_STORE_PATH = (
    PROJECT_ROOT
    / "Knowledge_Base_RAG"
    / "authority"
    / "vector_store"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def create_authority_chunks(documents):

    chunks = []

    for document in documents:

        text = document.page_content
        start = 0

        while start < len(text):

            end = min(start + CHUNK_SIZE, len(text))

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata=document.metadata.copy()
                    )
                )

            if end >= len(text):
                break

            start = end - CHUNK_OVERLAP

    return chunks


def build_authority_vector_store():

    documents = load_authority_documents()

    if not documents:
        raise RuntimeError(
            "No authority knowledge-base documents found."
        )

    chunks = create_authority_chunks(documents)

    if not chunks:
        raise RuntimeError(
            "No authority document chunks were created."
        )

    print(
        f"Loaded {len(documents)} documents "
        f"and created {len(chunks)} chunks."
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    AUTHORITY_VECTOR_STORE_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_store.save_local(
        str(AUTHORITY_VECTOR_STORE_PATH)
    )

    print(
        "Authority vector store saved to:",
        AUTHORITY_VECTOR_STORE_PATH
    )

    return vector_store


if __name__ == "__main__":
    build_authority_vector_store()