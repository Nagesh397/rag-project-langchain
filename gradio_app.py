import json
import logging

import gradio as gr

from rag.chains import RAGService
from rag.config import get_settings
from rag.embeddings import create_embeddings
from rag.evaluation import EvaluationRunner
from rag.retrieval import RetrievalService
from rag.vectorstore import create_vectorstore

settings = get_settings()
logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s")
store = create_vectorstore(settings, create_embeddings(settings))
rag = RAGService(RetrievalService(store, settings), settings)


def ask(question: str) -> tuple[str, str, str]:
    if not question.strip():
        return "Enter a question.", "[]", "{}"
    response = rag.ask(question)
    return response.answer, json.dumps(response.sources, indent=2), json.dumps(response.metadata, indent=2)


def evaluate() -> tuple[str, str]:
    result = EvaluationRunner(rag, settings).run()
    return json.dumps(result["aggregate"], indent=2), json.dumps(result["results"], indent=2)


with gr.Blocks(title="Hospital Policy RAG") as demo:
    gr.Markdown("# Hospital Policy RAG")
    with gr.Tab("RAG Playground"):
        question = gr.Textbox(label="Question")
        run = gr.Button("Run RAG", variant="primary")
        answer = gr.Markdown(label="Answer")
        sources = gr.Code(label="Sources", language="json")
        metadata = gr.Code(label="Retrieval metadata", language="json")
        run.click(ask, question, [answer, sources, metadata])
    with gr.Tab("Evaluation"):
        evaluate_button = gr.Button("Run evaluation")
        metrics = gr.Code(label="Aggregate metrics", language="json")
        cases = gr.Code(label="Cases", language="json")
        evaluate_button.click(evaluate, outputs=[metrics, cases])


if __name__ == "__main__":
    demo.launch(server_name=settings.gradio_host, server_port=settings.gradio_port)
