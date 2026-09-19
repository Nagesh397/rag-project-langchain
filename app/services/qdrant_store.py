"""Qdrant access kept behind a small service boundary."""

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import Settings


class QdrantStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )

    def ensure_collection(self) -> None:
        collections = {item.name for item in self.client.get_collections().collections}
        if self.settings.qdrant_collection not in collections:
            self.client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=VectorParams(size=self.settings.vector_size, distance=Distance.COSINE),
            )

    def search(self, vector: list[float], limit: int):
        return self.client.query_points(
            collection_name=self.settings.qdrant_collection,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points

    def upsert(self, points: list[PointStruct]) -> None:
        self.client.upsert(collection_name=self.settings.qdrant_collection, points=points)
