"""Retrieve approved document context for a user question."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ollama_client import OllamaClient
from app.services.qdrant_store import QdrantStore


@dataclass(frozen=True)
class RetrievalResult:
    context: str
    sources: list[dict]


class Retriever:
    def __init__(self, ollama: OllamaClient, qdrant: QdrantStore, limit: int) -> None:
        self.ollama = ollama
        self.qdrant = qdrant
        self.limit = limit

    async def retrieve(self, question: str) -> RetrievalResult:
        vector = await self.ollama.embed(question)
        hits = self.qdrant.search(vector, self.limit)
        sources = [hit.payload for hit in hits if hit.payload]
        context = "\n\n".join(source.get("text", "") for source in sources)
        return RetrievalResult(context=context, sources=sources)