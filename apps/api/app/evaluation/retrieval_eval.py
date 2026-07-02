import json
from pathlib import Path
from typing import Dict, List

from app.chunking.loader import load_chunks_from_file
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.reranking.reranker import CrossEncoderReranker
from app.retrieval.bm25_index import BM25Index, filter_chunks
from app.retrieval.hybrid_search import reciprocal_rank_fusion
from app.retrieval.schemas import SearchRequest, SearchResult
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


def summarize_strategy(strategy_name: str, per_query_results: List[Dict], top_k: int) -> Dict:
    average_hit_at_k = sum(
        item["metrics"]["hit_at_k"] for item in per_query_results
    ) / len(per_query_results)

    average_precision_at_k = sum(
        item["metrics"]["precision_at_k"] for item in per_query_results
    ) / len(per_query_results)

    return {
        "strategy": strategy_name,
        "top_k": top_k,
        "query_count": len(per_query_results),
        "average_hit_at_k": round(average_hit_at_k, 4),
        "average_precision_at_k": round(average_precision_at_k, 4),
        "per_query_results": per_query_results,
    }


def evaluate_retrieval_strategies(
    eval_path: str,
    chunks_path: str,
    top_k: int = 5,
    dense_k: int = 20,
    bm25_k: int = 20,
    rerank_top_k: int = 5,
    use_reranker: bool = True,
) -> Dict:
    eval_items = load_eval_set(eval_path)
    chunks = load_chunks_from_file(chunks_path)

    filtered_chunks = filter_chunks(
        chunks=chunks,
        source_type="scientific_paper",
        trust_level="verified",
        include_references=False,
    )

    embedding_provider = SentenceTransformerEmbeddingProvider()
    vector_store = QdrantVectorStore()
    bm25_index = BM25Index(filtered_chunks)
    reranker = CrossEncoderReranker() if use_reranker else None

    strategy_results = {
        "dense": [],
        "bm25": [],
        "hybrid": [],
        "reranked": [],
    }

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

        bm25_results = bm25_index.search(
            query=query,
            top_k=bm25_k,
        )

        hybrid_results = reciprocal_rank_fusion(
            dense_results=dense_results,
            bm25_results=bm25_results,
            top_k=max(top_k, dense_k, bm25_k),
        )

        if reranker:
            reranked_results = reranker.rerank(
                query=query,
                results=hybrid_results,
                top_k=rerank_top_k,
            )
        else:
            reranked_results = []

        strategy_to_results = {
            "dense": dense_results[:top_k],
            "bm25": bm25_results[:top_k],
            "hybrid": hybrid_results[:top_k],
            "reranked": reranked_results[:top_k],
        }

        for strategy_name, results in strategy_to_results.items():
            if strategy_name == "reranked" and not use_reranker:
                continue

            metrics = compute_section_metrics(
                results=results,
                relevant_sections=relevant_sections,
                top_k=top_k,
            )

            strategy_results[strategy_name].append(
                {
                    "query": query,
                    "relevant_sections": relevant_sections,
                    "metrics": metrics,
                    "retrieved_sections": [
                        result.section for result in results[:top_k]
                    ],
                    "retrieved_chunk_indices": [
                        result.chunk_index for result in results[:top_k]
                    ],
                }
            )

    final_results = {}

    for strategy_name, per_query_results in strategy_results.items():
        if not per_query_results:
            continue

        final_results[strategy_name] = summarize_strategy(
            strategy_name=strategy_name,
            per_query_results=per_query_results,
            top_k=top_k,
        )

    return {
        "top_k": top_k,
        "dense_k": dense_k,
        "bm25_k": bm25_k,
        "rerank_top_k": rerank_top_k,
        "strategy_comparison": final_results,
    }


def export_eval_report(results: Dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    return str(path)
