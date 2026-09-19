"""FastAPI entry point for the hospital RAG service."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.core.config import load_settings
from app.services.ollama_client import OllamaClient
from app.services.qdrant_store import QdrantStore
from app.services.retrieval import Retriever

settings = load_settings()
ollama = OllamaClient(settings)
qdrant = QdrantStore(settings)
retriever = Retriever(ollama, qdrant, settings.max_retrieval_results)


@asynccontextmanager
async def lifespan(_: FastAPI):
    qdrant.ensure_collection()
    yield


app = FastAPI(title="Hospital Knowledge API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_methods=["*"], allow_headers=["*"])


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "hospital-knowledge-api"}


@app.post("/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        result = await retriever.retrieve(request.question)
        if not result.context:
            return QueryResponse(answer="I could not find relevant approved content.", sources=[])
        answer = await ollama.answer(request.question, result.context)
        return QueryResponse(answer=answer, sources=result.sources)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="RAG dependencies are unavailable") from exc
