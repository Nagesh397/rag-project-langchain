from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from rag.config import Settings


class RetrievalService:
    def __init__(self, vectorstore: VectorStore, settings: Settings) -> None:
        self.vectorstore = vectorstore
        self.settings = settings

    def retrieve(self, question: str) -> list[Document]:
        if self.settings.search_type == "mmr":
            return self.vectorstore.max_marginal_relevance_search(question, k=self.settings.top_k)
        if self.settings.search_type == "similarity_score_threshold":
            retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": self.settings.top_k, "score_threshold": self.settings.score_threshold or 0.0})
            return retriever.invoke(question)
        return self.vectorstore.similarity_search(question, k=self.settings.top_k)
