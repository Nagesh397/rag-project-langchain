# Hospital Knowledge Assistant

Local-first hospital policy RAG application using Gradio, FastAPI, Ollama, and Qdrant.

## Structure

```text
app/
  api/       FastAPI routes
  core/      environment-backed configuration
  services/  Ollama, Qdrant, and ingestion boundaries
  ui/        Gradio interface
data/        runtime data, never committed
knowledge_base/ five approved starter policy documents
scripts/     operational commands
docker/      service Dockerfiles
config.yml   safe defaults and environment references
.env         local secrets and deployment values, never committed
```

## Configuration and secrets

Copy `.env.example` to `.env` and replace the placeholder values. Do not put credentials in `config.yml`, source code, Markdown documents, or Dockerfiles. The application loads `.env`, reads `config.yml`, and resolves `${VARIABLE:default}` references at startup. In Docker, service names such as `qdrant` and `ollama` are used; outside Docker, use `localhost`.

## Run locally with Docker

```powershell
Copy-Item .env.example .env
# Edit .env and set a strong QDRANT_API_KEY if Qdrant authentication is enabled.
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec api python scripts/ingest_knowledge_base.py
```

Open Gradio at http://localhost:7860 and the API health check at http://localhost:8000/health.

## Run without Docker

Install Python 3.12+, create a virtual environment, install `requirements.txt`, set `.env` with `QDRANT_HOST=localhost` and `OLLAMA_BASE_URL=http://localhost:11434`, then start Qdrant and Ollama separately. Run `uvicorn app.api.main:app --reload` and `python -m app.ui.gradio_app` in separate terminals.

## Security boundary

This starter is intended for approved, non-production policy content. It is not clinical decision support and must not be used to diagnose, prescribe, or expose patient records without completing authentication, authorization, audit, encryption, retention, threat modeling, and clinical safety review.
# Hospital-Management
