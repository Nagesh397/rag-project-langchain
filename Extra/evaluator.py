"""Gradio dashboard for aggregate hospital RAG evaluation."""

from __future__ import annotations

from collections import defaultdict
import os
from pathlib import Path
import sys

import gradio as gr

# Allow `python Extra/evaluator.py` to import the repository packages.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import load_settings
from app.services.ollama_client import OllamaClient
from app.services.qdrant_store import QdrantStore
from app.services.retrieval import Retriever
from Extra.evaluation.eval import evaluate_all_answers, evaluate_all_retrieval


RETRIEVAL_THRESHOLDS = {"mrr": (0.90, 0.75), "ndcg": (0.90, 0.75), "coverage": (90.0, 75.0)}
ANSWER_THRESHOLDS = {"accuracy": (4.5, 4.0), "completeness": (4.5, 4.0), "relevance": (4.5, 4.0)}


def build_retriever() -> tuple[Retriever, OllamaClient]:
    settings = load_settings()
    ollama = OllamaClient(settings)
    qdrant = QdrantStore(settings)
    qdrant.ensure_collection()
    return Retriever(ollama, qdrant, settings.max_retrieval_results), ollama


def metric_color(value: float, metric: str) -> str:
    green, amber = RETRIEVAL_THRESHOLDS.get(metric, ANSWER_THRESHOLDS.get(metric, (5.0, 4.0)))
    return "green" if value >= green else "orange" if value >= amber else "red"


def metric_html(label: str, value: float, metric: str, suffix: str = "") -> str:
    return (
        f'<div style="padding:12px;margin:8px 0;border-left:5px solid {metric_color(value, metric)};'
        f'background:#f5f5f5;border-radius:6px"><div>{label}</div>'
        f'<strong style="font-size:25px;color:{metric_color(value, metric)}">{value:.2f}{suffix}</strong></div>'
    )


def category_table_html(category_scores: dict[str, list[float]], label: str) -> str:
    rows = "".join(
        f"<tr><td>{category}</td><td>{sum(scores) / len(scores):.3f}</td></tr>"
        for category, scores in category_scores.items()
    )
    return (
        f'<table style="width:100%;border-collapse:collapse"><caption>{label}</caption>'
        '<thead><tr><th style="text-align:left">Category</th>'
        '<th style="text-align:left">Average</th></tr></thead>'
        f"<tbody>{rows}</tbody></table>"
    )


async def run_retrieval_evaluation(progress=gr.Progress()):
    empty_chart = "<p>No category results yet.</p>"
    yield "Status: evaluation started...", "Run in progress.", empty_chart
    try:
        retriever, _ = build_retriever()
        totals = defaultdict(float)
        category_scores: dict[str, list[float]] = defaultdict(list)
        count = 0
        async for test, result, progress_value in evaluate_all_retrieval(retriever):
            count += 1
            totals["mrr"] += result.mrr
            totals["ndcg"] += result.ndcg
            totals["coverage"] += result.keyword_coverage
            category_scores[test.category].append(result.mrr)
            progress(progress_value, desc=f"Retrieval test {count} running")

        if not count:
            yield "No retrieval tests found.", "<p>No retrieval tests found.</p>", empty_chart
            return
        averages = {name: value / count for name, value in totals.items()}
        html = "".join(
            [
                metric_html("Mean Reciprocal Rank (MRR)", averages["mrr"], "mrr"),
                metric_html("Normalized DCG", averages["ndcg"], "ndcg"),
                metric_html("Keyword Coverage", averages["coverage"], "coverage", "%"),
                f"<p>Evaluation complete: {count} tests</p>",
            ]
        )
        chart = category_table_html(category_scores, "Average MRR by Category")
        yield f"Retrieval evaluation complete: {count} tests.", html, chart
    except Exception as exc:
        yield f"Retrieval evaluation failed: {exc}", "<p>Evaluation failed. See status above.</p>", empty_chart


async def run_answer_evaluation(progress=gr.Progress()):
    empty_chart = "<p>No category results yet.</p>"
    yield "Status: evaluation started...", "Run in progress.", empty_chart
    try:
        retriever, ollama = build_retriever()
        totals = defaultdict(float)
        category_scores: dict[str, list[float]] = defaultdict(list)
        count = 0
        async for test, result, progress_value in evaluate_all_answers(retriever, ollama):
            count += 1
            totals["accuracy"] += result.accuracy
            totals["completeness"] += result.completeness
            totals["relevance"] += result.relevance
            category_scores[test.category].append(result.accuracy)
            progress(progress_value, desc=f"Answer test {count} running")

        if not count:
            yield "No answer tests found.", "<p>No answer tests found.</p>", empty_chart
            return
        averages = {name: value / count for name, value in totals.items()}
        html = "".join(
            [
                metric_html("Accuracy", averages["accuracy"], "accuracy", "/5"),
                metric_html("Completeness", averages["completeness"], "completeness", "/5"),
                metric_html("Relevance", averages["relevance"], "relevance", "/5"),
                f"<p>Evaluation complete: {count} tests</p>",
            ]
        )
        chart = category_table_html(category_scores, "Average Accuracy by Category")
        yield f"Answer evaluation complete: {count} tests.", html, chart
    except Exception as exc:
        yield f"Answer evaluation failed: {exc}", "<p>Evaluation failed. See status above.</p>", empty_chart


with gr.Blocks(title="Hospital RAG Evaluation Dashboard") as app:
    gr.Markdown("# Hospital RAG Evaluation Dashboard")
    gr.Markdown("Evaluate retrieval quality and answer quality using the configured Ollama models.")

    gr.Markdown("## Retrieval Evaluation")
    retrieval_button = gr.Button("Run Retrieval Evaluation", variant="primary")
    retrieval_status = gr.Markdown("Status: not started")
    with gr.Row():
        retrieval_metrics = gr.HTML("Run the evaluation to view metrics.")
        retrieval_chart = gr.HTML("<p>No category results yet.</p>")
    retrieval_button.click(
        run_retrieval_evaluation,
        outputs=[retrieval_status, retrieval_metrics, retrieval_chart],
    )

    gr.Markdown("## Answer Evaluation")
    answer_button = gr.Button("Run Answer Evaluation", variant="primary")
    answer_status = gr.Markdown("Status: not started")
    with gr.Row():
        answer_metrics = gr.HTML("Run the evaluation to view metrics.")
        answer_chart = gr.HTML("<p>No category results yet.</p>")
    answer_button.click(
        run_answer_evaluation,
        outputs=[answer_status, answer_metrics, answer_chart],
    )


if __name__ == "__main__":
    app.queue()
    app.launch(
        inbrowser=True,
        server_name="127.0.0.1",
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    )
