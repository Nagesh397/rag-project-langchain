from pathlib import Path

import pytest

from rag.config import get_settings


def test_settings_are_environment_driven(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-test")
    monkeypatch.setenv("TOP_K", "7")
    settings = get_settings(tmp_path)
    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-test"
    assert settings.top_k == 7


def test_chunk_overlap_must_be_smaller(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHUNK_SIZE", "100")
    monkeypatch.setenv("CHUNK_OVERLAP", "100")
    with pytest.raises(ValueError, match="CHUNK_OVERLAP"):
        get_settings(tmp_path)
