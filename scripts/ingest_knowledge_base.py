"""Run: python scripts/ingest_knowledge_base.py"""

import asyncio

from app.core.config import load_settings
from app.services.ingestion import KnowledgeBaseIngestor
from app.services.ollama_client import OllamaClient
from app.services.qdrant_store import QdrantStore


async def main() -> None:
    settings = load_settings()
    count = await KnowledgeBaseIngestor(settings, OllamaClient(settings), QdrantStore(settings)).ingest_directory(
        settings.documents_path
    )
    print(f"Indexed {count} knowledge-base chunks")


if __name__ == "__main__":
    asyncio.run(main())
