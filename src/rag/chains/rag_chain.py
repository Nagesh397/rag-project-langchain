from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter

from langchain_core.documents import Document

from rag.config import Settings
from rag.llm.factory import create_llm
from rag.prompting import rag_prompt
from rag.retrieval import RetrievalService


@dataclass(frozen=True)
class RAGResponse:
    answer: str
    sources: list[dict]
    retrieved_documents: list[dict]
    metadata: dict

    def as_dict(self) -> dict:
        return asdict(self)


class RAGService:
    def __init__(self, retrieval: RetrievalService, settings: Settings) -> None:
        self.retrieval = retrieval
        self.settings = settings
        self.llm = create_llm(settings)

    def ask(self, question: str) -> RAGResponse:
        started = perf_counter()
        documents = self.retrieval.retrieve(question)
        context = "\n\n".join(f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}" for doc in documents)
        response = (rag_prompt | self.llm).invoke({"context": context, "question": question})
        answer = response.content if isinstance(response.content, str) else str(response.content)
        sources = [dict(document.metadata) for document in documents]
        return RAGResponse(answer=answer.strip(), sources=sources, retrieved_documents=[self._document_dict(doc) for doc in documents], metadata={"provider": self.settings.llm_provider, "model": self.settings.llm_model, "retrieved_count": len(documents), "latency_ms": round((perf_counter() - started) * 1000, 2)})

    @staticmethod
    def _document_dict(document: Document) -> dict:
        return {"content": document.page_content, "metadata": dict(document.metadata)}
