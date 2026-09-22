from __future__ import annotations

from langchain_core.embeddings import Embeddings

from rag.config import Settings


def create_embeddings(settings: Settings) -> Embeddings:
    if settings.embedding_provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(model=settings.embedding_model, base_url=settings.ollama_base_url)
    if settings.embedding_provider in {"huggingface", "hf"}:
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=settings.embedding_model)
    if settings.embedding_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
