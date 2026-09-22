from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from rag.chains import RAGService
from rag.config import Settings
from rag.evaluation.metrics import retrieval_metrics


class EvaluationRunner:
    def __init__(self, rag: RAGService, settings: Settings) -> None:
        self.rag = rag
        self.settings = settings

    def run(self, dataset: Path | None = None) -> dict:
        path = dataset or self.settings.resolved(self.settings.evaluation_dataset)
        cases = json.loads(path.read_text(encoding="utf-8"))
        results = []
        for case in cases:
            response = self.rag.ask(case["question"])
            sources = [item.get("source", "") for item in response.sources]
            metrics = retrieval_metrics(case.get("expected_context", case.get("expected_sources", [])), sources, self.settings.top_k)
            results.append({"question": case["question"], "ground_truth": case.get("ground_truth", ""), "answer": response.answer, "sources": response.sources, "metrics": metrics})
        aggregate = {key: sum(item["metrics"][key] for item in results) / len(results) for key in ("recall_at_k", "precision_at_k", "mrr")} if results else {}
        output = {"timestamp": datetime.now(UTC).isoformat(), "dataset": str(path), "aggregate": aggregate, "results": results}
        output_dir = self.settings.resolved(self.settings.evaluation_output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "latest.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
        return output
