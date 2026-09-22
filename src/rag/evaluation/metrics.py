from __future__ import annotations


def retrieval_metrics(expected_sources: list[str], retrieved_sources: list[str], k: int) -> dict[str, float]:
    expected = {source.lower() for source in expected_sources}
    retrieved = [source.lower() for source in retrieved_sources[:k]]
    hits = [index for index, source in enumerate(retrieved, start=1) if source in expected]
    return {
        "recall_at_k": len(set(retrieved) & expected) / len(expected) if expected else 0.0,
        "precision_at_k": len(hits) / len(retrieved) if retrieved else 0.0,
        "mrr": 1 / hits[0] if hits else 0.0,
    }
