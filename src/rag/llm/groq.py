from langchain_groq import ChatGroq

from rag.config import Settings


def create(settings: Settings) -> ChatGroq:
    return ChatGroq(model=settings.llm_model, temperature=settings.llm_temperature, timeout=settings.llm_timeout, max_retries=2, api_key=settings.groq_api_key)
