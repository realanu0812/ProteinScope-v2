from typing import List

from sentence_transformers import CrossEncoder

from app.retrieval.schemas import HybridSearchResult


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self._model_name = model_name
        self.model = CrossEncoder(model_name)

    def model_name(self) -> str:
        return self._model_name

    def rerank(
        self,
        query: str,
        results: List[HybridSearchResult],
        top_k: int = 5,
    ) -> List[HybridSearchResult]:
        if not results:
            return []

        pairs = [(query, result.text) for result in results]
        scores = self.model.predict(pairs)

        scored_results = []

        for result, score in zip(results, scores):
            updated_result = result.model_copy(update={"score": float(score)})
            scored_results.append(updated_result)

        return sorted(
            scored_results,
            key=lambda item: item.score,
            reverse=True,
        )[:top_k]
