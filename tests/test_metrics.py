from rag.evaluation.metrics import retrieval_metrics


def test_retrieval_metrics() -> None:
    result = retrieval_metrics(["a.md"], ["other.md", "a.md"], 2)
    assert result == {"recall_at_k": 1.0, "precision_at_k": 0.5, "mrr": 0.5}
