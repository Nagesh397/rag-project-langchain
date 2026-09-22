from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from rag.config import Settings


def create_llm(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "openai":
        from .openai import create
    elif settings.llm_provider in {"gemini", "google"}:
        from .gemini import create
    elif settings.llm_provider == "groq":
        from .groq import create
    elif settings.llm_provider == "ollama":
        from .ollama import create
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    return create(settings)
