from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

from rag.processing.cleaning import clean_text
from rag.processing.metadata import enrich_metadata


def load_documents(directory: Path) -> list[Document]:
    if not directory.exists():
        raise FileNotFoundError(f"Document directory does not exist: {directory}")
    loader = DirectoryLoader(str(directory), glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    documents: list[Document] = []
    for document in loader.load():
        source = Path(document.metadata.get("source", "unknown.md"))
        document_id = hashlib.sha256(source.name.encode("utf-8")).hexdigest()[:16]
        normalized = Document(page_content=clean_text(document.page_content), metadata=document.metadata)
        documents.append(enrich_metadata(normalized, source, document_id))
    return documents
