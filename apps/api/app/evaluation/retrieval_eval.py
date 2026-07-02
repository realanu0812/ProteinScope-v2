import json
from pathlib import Path
from typing import Dict, List

from app.chunking.loader import load_chunks_from_file
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.retrieval.bm25_index import BM25Index, filter_chunks
from app.retrieval.hybrid_search import reciprocal_rank_fusion
from app.retrieval.schemas import HybridSearchRequest, SearchRequest, SearchResult
from app.vector_store.qdrant_store import QdrantVectorStore


def load_eval_set(eval_path: str) -> List[Dict]:
    with Path(eval_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def compute_section_metrics(
    results: List[SearchResult],
    relevant_sections: List[str],
    top_k: int,
) -> Dict:
    top_results = results[:top_k]

    relevant_count = sum(
        1 for result in top_results
        if result.section in relevant_sections
    )

    hit_at_k = 1 if relevant_count > 0 else 0
    precision_at_k = relevant_count / top_k if top_k > 0 else 0

    return {
        "hit_at_k": hit_at_k,
        "precision_at_k": round(precision_at_k, 4),
        "relevant_count": relevant_count,
    }


def evaluate_hybrid_retrieval(
    eval_path: str,
    chunks_path: str,
    top_k: int = 5,
    dense_k: int = 20,
    bm25_k: int = 20,
) -> Dict:
    eval_items = load_eval_set(eval_path)
    chunks = load_chunks_from_file(chunks_path)

    embedding_provider = SentenceTransformerEmbeddingProvider()
    vector_store = QdrantVectorStore()

    per_query_results = []

    for item in eval_items:
        query = item["query"]
        relevant_sections = item["relevant_sections"]

        query_vector = embedding_provider.embed_texts([query])[0]

        dense_request = SearchRequest(
            query=query,
            top_k=dense_k,
            source_type="scientific_paper",
            trust_level="verified",
            include_references=False,
        )

        dense_results = vector_store.search(
            query_vector=query_vector,
            request=dense_request,
        )

        filtered_chunks = filter_chunks(
            chunks=chunks,
            source_type="scientific_paper",
            trust_level="verified",
            include_references=False,
        )

        bm25_index = BM25Index(filtered_chunks)
        bm25_results = bm25_index.search(
            query=query,
            top_k=bm25_k,
        )

        hybrid_results = reciprocal_rank_fusion(
            dense_results=dense_results,
            bm25_results=bm25_results,
            top_k=top_k,
        )

        metrics = compute_section_metrics(
            results=hybrid_results,
            relevant_sections=relevant_sections,
            top_k=top_k,
        )

        per_query_results.append(
            {
                "query": query,
                "relevant_sections": relevant_sections,
                "metrics": metrics,
                "retrieved_sections": [
                    result.section for result in hybrid_results[:top_k]
                ],
                "retrieved_chunk_indices": [
                    result.chunk_index for result in hybrid_results[:top_k]
                ],
            }
        )

    average_hit_at_k = sum(
        item["metrics"]["hit_at_k"] for item in per_query_results
    ) / len(per_query_results)

    average_precision_at_k = sum(
        item["metrics"]["precision_at_k"] for item in per_query_results
    ) / len(per_query_results)

    return {
        "strategy": "hybrid",
        "top_k": top_k,
        "dense_k": dense_k,
        "bm25_k": bm25_k,
        "query_count": len(per_query_results),
        "average_hit_at_k": round(average_hit_at_k, 4),
        "average_precision_at_k": round(average_precision_at_k, 4),
        "per_query_results": per_query_results,
    }


def export_eval_report(results: Dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    return str(path)
