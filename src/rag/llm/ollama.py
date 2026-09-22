from langchain_ollama import ChatOllama

from rag.config import Settings


def create(settings: Settings) -> ChatOllama:
    return ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url, temperature=settings.llm_temperature, client_kwargs={"timeout": settings.llm_timeout})
