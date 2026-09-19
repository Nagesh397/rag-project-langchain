"""Application configuration with .env-backed YAML interpolation."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::([^}]*))?\}")


@dataclass(frozen=True)
class Settings:
    qdrant_host: str
    qdrant_port: int
    qdrant_api_key: str | None
    qdrant_collection: str
    vector_size: int
    ollama_base_url: str
    llm_model: str
    embedding_model: str
    documents_path: Path
    audit_log_path: Path
    max_retrieval_results: int
    allowed_origins: list[str]


def _resolve(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _resolve(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        return os.getenv(match.group(1), match.group(2) or "")

    resolved = _ENV_PATTERN.sub(replace, value)
    if resolved.isdigit():
        return int(resolved)
    return resolved


def load_settings(config_path: Path | None = None) -> Settings:
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    path = config_path or root / "config.yml"
    with path.open("r", encoding="utf-8") as config_file:
        raw = _resolve(yaml.safe_load(config_file))

    qdrant = raw["qdrant"]
    ollama = raw["ollama"]
    application = raw["application"]
    storage = raw["storage"]
    api_key = qdrant.get("api_key") or None
    return Settings(
        qdrant_host=qdrant["host"],
        qdrant_port=int(qdrant["port"]),
        qdrant_api_key=api_key,
        qdrant_collection=qdrant["collection_name"],
        vector_size=int(qdrant["vector_size"]),
        ollama_base_url=ollama["base_url"].rstrip("/"),
        llm_model=ollama["llm_model"],
        embedding_model=ollama["embedding_model"],
        documents_path=root / storage["documents_path"],
        audit_log_path=root / storage["audit_log_path"],
        max_retrieval_results=int(application["max_retrieval_results"]),
        allowed_origins=[item.strip() for item in application["allowed_origins"].split(",") if item.strip()],
    )
