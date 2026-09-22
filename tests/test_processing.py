from pathlib import Path

from langchain_core.documents import Document

from rag.processing import clean_text, enrich_metadata


def test_clean_text_normalizes_whitespace() -> None:
    assert clean_text("  one\r\n\r\n\r\ntwo  ") == "one\n\ntwo"


def test_metadata_contains_stable_source_identity() -> None:
    document = enrich_metadata(Document(page_content="policy"), Path("policy.md"), "abc123")
    assert document.metadata["document_id"] == "abc123"
    assert document.metadata["source"] == "policy.md"
