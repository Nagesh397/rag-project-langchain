from __future__ import annotations

import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import Settings
from rag.embeddings.factory import create_embeddings
from rag.ingestion.loaders import load_documents
from rag.vectorstore.factory import create_vectorstore

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def split_documents(self, documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            add_start_index=True,
        )
        chunks = splitter.split_documents(documents)
        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"{chunk.metadata['document_id']}-{index}"
        return chunks

    def ingest_directory(self, directory: Path | None = None) -> int:
        source = directory or self.settings.resolved(self.settings.documents_path)
        documents = load_documents(source)
        chunks = self.split_documents(documents)
        if not chunks:
            logger.warning("No documents found in %s", source)
            return 0
        create_vectorstore(self.settings, create_embeddings(self.settings), create=True, documents=chunks)
        logger.info("Ingested %d documents into %d chunks", len(documents), len(chunks))
        return len(chunks)
