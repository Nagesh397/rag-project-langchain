from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from rag.config import Settings


def create_vectorstore(settings: Settings, embeddings: Embeddings, create: bool = False, documents: list | None = None) -> VectorStore:
    if settings.vector_store != "qdrant":
        raise ValueError(f"Unsupported vector store: {settings.vector_store}")
    from langchain_qdrant import QdrantVectorStore

    if create:
        if not documents:
            raise ValueError("documents are required when creating a vector store")
        try:
            store = QdrantVectorStore.from_existing_collection(
                embedding=embeddings,
                collection_name=settings.collection_name,
                url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
                api_key=settings.qdrant_api_key,
            )
            store.add_documents(documents)
            return store
        except Exception as error:
            if "doesn't exist" not in str(error).lower() and "not found" not in str(error).lower():
                raise
            return QdrantVectorStore.from_documents(
                documents,
                embedding=embeddings,
                collection_name=settings.collection_name,
                url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
                api_key=settings.qdrant_api_key,
            )
    return QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=settings.collection_name,
        url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
        api_key=settings.qdrant_api_key,
    )
