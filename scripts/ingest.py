import logging

from rag.config import get_settings
from rag.ingestion import IngestionService

if __name__ == "__main__":
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s")
    print(f"Ingested {IngestionService(settings).ingest_directory()} chunks")
