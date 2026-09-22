from pathlib import Path

from langchain_core.documents import Document


def enrich_metadata(document: Document, source_path: Path, document_id: str) -> Document:
    metadata = dict(document.metadata)
    metadata.update({
        "source": source_path.name,
        "filename": source_path.name,
        "title": source_path.stem,
        "document_id": document_id,
    })
    return Document(page_content=document.page_content, metadata=metadata)
