"""Markdown knowledge-base ingestion for the first project milestone."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from qdrant_client.models import PointStruct

from app.core.config import Settings
from app.services.ollama_client import OllamaClient
from app.services.qdrant_store import QdrantStore


class KnowledgeBaseIngestor:
    def __init__(self, settings: Settings, ollama: OllamaClient, qdrant: QdrantStore) -> None:
        self.settings = settings
        self.ollama = ollama
        self.qdrant = qdrant

    @staticmethod
    def _chunks(text: str) -> list[str]:
        sections = re.split(r"\n(?=<!-- Page \d+ -->|## )", text)
        return [section.strip() for section in sections if len(section.strip()) > 80]

    async def ingest_directory(self, directory: Path) -> int:
        self.qdrant.ensure_collection()
        points: list[PointStruct] = []
        for document in sorted(directory.glob("*.md")):
            text = document.read_text(encoding="utf-8")
            for index, chunk in enumerate(self._chunks(text)):
                vector = await self.ollama.embed(chunk)
                point_id = hashlib.sha256(f"{document.name}:{index}".encode()).hexdigest()[:32]
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={"text": chunk, "title": document.stem, "source": document.name, "chunk": index},
                    )
                )
        if points:
            self.qdrant.upsert(points)
        return len(points)
