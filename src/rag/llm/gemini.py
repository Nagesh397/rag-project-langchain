from langchain_google_genai import ChatGoogleGenerativeAI

from rag.config import Settings


def create(settings: Settings) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=settings.llm_model, temperature=settings.llm_temperature, timeout=settings.llm_timeout, max_retries=2, google_api_key=settings.google_api_key)
