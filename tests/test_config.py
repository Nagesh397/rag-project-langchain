from pathlib import Path

from app.core.config import load_settings


def test_config_resolves_environment_values(monkeypatch, tmp_path: Path):
    config = tmp_path / "config.yml"
    config.write_text(
        """
qdrant:
  host: "${QDRANT_HOST:localhost}"
  port: "${QDRANT_PORT:6333}"
  api_key: "${QDRANT_API_KEY:}"
  collection_name: "${QDRANT_COLLECTION:test_collection}"
  vector_size: 768
ollama:
  base_url: "${OLLAMA_BASE_URL:http://localhost:11434}"
  llm_model: "${OLLAMA_LLM_MODEL:test-llm}"
  embedding_model: "${OLLAMA_EMBEDDING_MODEL:test-embed}"
application:
  allowed_origins: "${ALLOWED_ORIGINS:http://localhost:7860}"
  max_retrieval_results: "${MAX_RETRIEVAL_RESULTS:5}"
storage:
  documents_path: "data/documents"
  audit_log_path: "data/audit/audit.log"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("QDRANT_HOST", "secure-qdrant")
    monkeypatch.setenv("QDRANT_API_KEY", "test-secret")
    settings = load_settings(config)
    assert settings.qdrant_host == "secure-qdrant"
    assert settings.qdrant_api_key == "test-secret"
    assert settings.qdrant_port == 6333
