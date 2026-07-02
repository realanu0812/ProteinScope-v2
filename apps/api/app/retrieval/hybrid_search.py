from typing import Dict, List

from app.retrieval.schemas import HybridSearchResult, SearchResult


RRF_K = 60


def reciprocal_rank_fusion(
    dense_results: List[SearchResult],
    bm25_results: List[SearchResult],
    top_k: int = 5,
) -> List[HybridSearchResult]:
    """
    Merges dense and BM25 results using Reciprocal Rank Fusion.

    RRF score:
        score += 1 / (k + rank)

    Why RRF?
    - Simple
    - Does not require score normalization
    - Works well when dense and BM25 scores are on different scales
    """

    fused: Dict[str, Dict] = {}

    for rank, result in enumerate(dense_results, start=1):
        if result.chunk_id not in fused:
            fused[result.chunk_id] = {
                "result": result,
                "dense_rank": None,
                "bm25_rank": None,
                "fusion_score": 0.0,
            }

        fused[result.chunk_id]["dense_rank"] = rank
        fused[result.chunk_id]["fusion_score"] += 1 / (RRF_K + rank)

    for rank, result in enumerate(bm25_results, start=1):
        if result.chunk_id not in fused:
            fused[result.chunk_id] = {
                "result": result,
                "dense_rank": None,
                "bm25_rank": None,
                "fusion_score": 0.0,
            }

        fused[result.chunk_id]["bm25_rank"] = rank
        fused[result.chunk_id]["fusion_score"] += 1 / (RRF_K + rank)

    ranked_items = sorted(
        fused.values(),
        key=lambda item: item["fusion_score"],
        reverse=True,
    )

    hybrid_results = []

    for item in ranked_items[:top_k]:
        result = item["result"]

        hybrid_results.append(
            HybridSearchResult(
                score=result.score,
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                chunk_index=result.chunk_index,
                source_type=result.source_type,
                trust_level=result.trust_level,
                section=result.section,
                start_page=result.start_page,
                end_page=result.end_page,
                text=result.text,
                dense_rank=item["dense_rank"],
                bm25_rank=item["bm25_rank"],
                fusion_score=item["fusion_score"],
            )
        )

    return hybrid_results
