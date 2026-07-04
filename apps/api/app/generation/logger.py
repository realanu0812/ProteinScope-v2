import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.generation.schemas import AnswerRequest, Citation
from app.retrieval.schemas import HybridSearchResult


def log_answer_event(
    request: AnswerRequest,
    answer: str,
    generator_model: str,
    citations: List[Citation],
    retrieved_context: List[HybridSearchResult],
    output_path: str = "outputs/generation/answer_logs.jsonl",
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": request.question,
        "generator_model": generator_model,
        "retrieval_strategy": "hybrid_dense_bm25_rrf",
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
        "answer": answer,
        "citations": [
            citation.model_dump()
            for citation in citations
        ],
        "retrieved_context": [
            {
                "rank": index + 1,
                "fusion_score": result.fusion_score,
                "dense_rank": result.dense_rank,
                "bm25_rank": result.bm25_rank,
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "section": result.section,
                "start_page": result.start_page,
                "end_page": result.end_page,
                "preview": result.text[:240].replace("\n", " "),
            }
            for index, result in enumerate(retrieved_context)
        ],
    }

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return str(path)
