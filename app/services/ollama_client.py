"""Small Ollama client used by both ingestion and retrieval."""

from __future__ import annotations

import httpx

from app.core.config import Settings


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.settings.ollama_base_url}/api/embed",
                json={"model": self.settings.embedding_model, "input": text},
            )
            response.raise_for_status()
            payload = response.json()
            return payload["embeddings"][0]

    async def answer(self, question: str, context: str) -> str:
        prompt = (
            "You are a hospital knowledge assistant. Answer only from the supplied context. "
            "If the context is insufficient, say so. Do not diagnose, prescribe, or invent facts.\n\n"
            f"Context:\n{context}\n\nQuestion:\n{question}"
        )
        async with httpx.AsyncClient(timeout=360) as client:
            response = await client.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json={
                    "model": self.settings.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {"num_predict": 256, "temperature": 0.1},
                },
            )
            response.raise_for_status()
            return response.json()["response"].strip()
