"""Minimal Gradio interface; all model and vector access stays in FastAPI."""

from __future__ import annotations

import os

import gradio as gr
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def ask_hospital_assistant(question: str):
    if not question.strip():
        yield "Please enter a question.", "", "Ready"
        return
    yield "", "", "Processing..."
    try:
        response = httpx.post(f"{API_BASE_URL}/v1/query", json={"question": question}, timeout=360)
        response.raise_for_status()
        payload = response.json()
        sources = "\n".join(f"- {source.get('title', 'Untitled')}" for source in payload["sources"])
        yield payload["answer"], sources or "No sources returned.", "Complete"
    except httpx.HTTPError:
        yield "The knowledge service is currently unavailable.", "", "Request failed"


with gr.Blocks(title="Hospital Knowledge Assistant") as demo:
    gr.Markdown("# Hospital Knowledge Assistant\nAnswers are grounded in approved hospital documents.")
    question = gr.Textbox(label="Question", placeholder="Ask about an approved hospital policy...")
    ask = gr.Button("Ask")
    status = gr.Markdown("Ready")
    answer = gr.Markdown(label="Answer")
    sources = gr.Markdown(label="Sources")
    ask.click(
        ask_hospital_assistant,
        inputs=question,
        outputs=[answer, sources, status],
        show_progress="full",
    )
    demo.queue()


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
