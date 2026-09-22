import json
import logging

from rag.chains import RAGService
from rag.config import get_settings
from rag.embeddings import create_embeddings
from rag.evaluation import EvaluationRunner
from rag.retrieval import RetrievalService
from rag.vectorstore import create_vectorstore

if __name__ == "__main__":
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s")
    store = create_vectorstore(settings, create_embeddings(settings))
    output = EvaluationRunner(RAGService(RetrievalService(store, settings), settings), settings).run()
    print(json.dumps(output["aggregate"], indent=2))
