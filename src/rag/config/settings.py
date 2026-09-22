from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    root: Path
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2:3b"
    llm_temperature: float = 0.1
    llm_timeout: float = 120.0
    openai_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    embedding_provider: str = "ollama"
    embedding_model: str = "nomic-embed-text"
    vector_store: str = "qdrant"
    vector_store_path: Path = field(default=Path("data/vectorstore"))
    collection_name: str = "hospital_knowledge"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    top_k: int = 5
    search_type: str = "similarity"
    score_threshold: float | None = None
    chunk_size: int = 900
    chunk_overlap: int = 150
    documents_path: Path = field(default=Path("data/documents/drive"))
    evaluation_dataset: Path = field(default=Path("Extra/evaluation/tests.json"))
    evaluation_output_path: Path = field(default=Path("evaluation/results"))
    log_level: str = "INFO"
    gradio_host: str = "127.0.0.1"
    gradio_port: int = 7860
    allowed_origins: list[str] = field(default_factory=list)

    def resolved(self, path: Path) -> Path:
        return path if path.is_absolute() else self.root / path


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def get_settings(root: Path | None = None) -> Settings:
    project_root = root or Path(__file__).resolve().parents[3]
    load_dotenv(project_root / ".env")
    settings = Settings(
        root=project_root,
        llm_provider=_env("LLM_PROVIDER", "ollama").lower(),
        llm_model=_env("LLM_MODEL", "llama3.2:3b"),
        llm_temperature=float(_env("LLM_TEMPERATURE", "0.1")),
        llm_timeout=float(_env("LLM_TIMEOUT", "120")),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        google_api_key=os.getenv("GOOGLE_API_KEY") or None,
        groq_api_key=os.getenv("GROQ_API_KEY") or None,
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        embedding_provider=_env("EMBEDDING_PROVIDER", "ollama").lower(),
        embedding_model=_env("EMBEDDING_MODEL", "nomic-embed-text"),
        vector_store=_env("VECTOR_STORE", "qdrant").lower(),
        vector_store_path=Path(_env("VECTOR_STORE_PATH", "data/vectorstore")),
        collection_name=_env("COLLECTION_NAME", "hospital_knowledge"),
        qdrant_host=_env("QDRANT_HOST", "localhost"),
        qdrant_port=int(_env("QDRANT_PORT", "6333")),
        qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
        top_k=int(_env("TOP_K", "5")),
        search_type=_env("SEARCH_TYPE", "similarity"),
        score_threshold=float(os.environ["SCORE_THRESHOLD"]) if os.getenv("SCORE_THRESHOLD") else None,
        chunk_size=int(_env("CHUNK_SIZE", "900")),
        chunk_overlap=int(_env("CHUNK_OVERLAP", "150")),
        documents_path=Path(_env("DOCUMENTS_PATH", "data/documents/drive")),
        evaluation_dataset=Path(_env("EVALUATION_DATASET", "Extra/evaluation/tests.json")),
        evaluation_output_path=Path(_env("EVALUATION_OUTPUT_PATH", "evaluation/results")),
        log_level=_env("LOG_LEVEL", "INFO"),
        gradio_host=_env("GRADIO_HOST", "127.0.0.1"),
        gradio_port=int(_env("GRADIO_PORT", "7860")),
        allowed_origins=[item.strip() for item in _env("ALLOWED_ORIGINS", "").split(",") if item.strip()],
    )
    if settings.chunk_overlap >= settings.chunk_size:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
    if settings.top_k < 1:
        raise ValueError("TOP_K must be at least 1")
    return settings
