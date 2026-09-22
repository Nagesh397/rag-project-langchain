from langchain_openai import ChatOpenAI

from rag.config import Settings


def create(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature, timeout=settings.llm_timeout, max_retries=2, api_key=settings.openai_api_key)
