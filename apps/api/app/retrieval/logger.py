import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.retrieval.schemas import HybridSearchRequest, HybridSearchResult, SearchRequest, SearchResult


def log_search_event(
    request: SearchRequest,
    results: List[SearchResult],
    output_path: str = "outputs/retrieval/search_logs.jsonl",
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": request.query,
        "top_k": request.top_k,
        "filters": {
            "document_id": request.document_id,
            "source_type": request.source_type,
            "trust_level": request.trust_level,
            "section": request.section,
            "include_references": request.include_references,
        },
        "result_count": len(results),
        "results": [
            {
                "score": result.score,
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "chunk_index": result.chunk_index,
                "source_type": result.source_type,
                "trust_level": result.trust_level,
                "section": result.section,
                "start_page": result.start_page,
                "end_page": result.end_page,
                "preview": result.text[:220].replace("\n", " "),
            }
            for result in results
        ],
    }

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return str(path)


def log_hybrid_search_event(
    request: HybridSearchRequest,
    dense_results: List[SearchResult],
    bm25_results: List[SearchResult],
    hybrid_results: List[HybridSearchResult],
    output_path: str = "outputs/retrieval/hybrid_search_logs.jsonl",
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": request.query,
        "top_k": request.top_k,
        "dense_k": request.dense_k,
        "bm25_k": request.bm25_k,
        "filters": {
            "document_id": request.document_id,
            "source_type": request.source_type,
            "trust_level": request.trust_level,
            "section": request.section,
            "include_references": request.include_references,
        },
        "dense_results": [
            {
                "rank": index + 1,
                "score": result.score,
                "chunk_id": result.chunk_id,
                "chunk_index": result.chunk_index,
                "section": result.section,
                "pages": f"{result.start_page}-{result.end_page}",
                "preview": result.text[:180].replace("\n", " "),
            }
            for index, result in enumerate(dense_results)
        ],
        "bm25_results": [
            {
                "rank": index + 1,
                "score": result.score,
                "chunk_id": result.chunk_id,
                "chunk_index": result.chunk_index,
                "section": result.section,
                "pages": f"{result.start_page}-{result.end_page}",
                "preview": result.text[:180].replace("\n", " "),
            }
            for index, result in enumerate(bm25_results)
        ],
        "hybrid_results": [
            {
                "rank": index + 1,
                "fusion_score": result.fusion_score,
                "dense_rank": result.dense_rank,
                "bm25_rank": result.bm25_rank,
                "chunk_id": result.chunk_id,
                "chunk_index": result.chunk_index,
                "section": result.section,
                "pages": f"{result.start_page}-{result.end_page}",
                "preview": result.text[:180].replace("\n", " "),
            }
            for index, result in enumerate(hybrid_results)
        ],
    }

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return str(path)
