from typing import List

from app.chunking.loader import load_chunks_from_file
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.generation.groq_provider import GroqGenerationProvider
from app.generation.logger import log_answer_event
from app.generation.prompt_builder import build_grounded_prompt
from app.generation.schemas import AnswerRequest, AnswerResponse, Citation
from app.retrieval.bm25_index import BM25Index, filter_chunks
from app.retrieval.hybrid_search import reciprocal_rank_fusion
from app.retrieval.schemas import SearchRequest
from app.vector_store.qdrant_store import QdrantVectorStore


def generate_grounded_answer(request: AnswerRequest) -> AnswerResponse:
    embedding_provider = SentenceTransformerEmbeddingProvider()
    query_vector = embedding_provider.embed_texts([request.question])[0]

    dense_request = SearchRequest(
        query=request.question,
        top_k=request.dense_k,
        document_id=request.document_id,
        source_type=request.source_type,
        trust_level=request.trust_level,
        section=request.section,
        include_references=request.include_references,
    )

    vector_store = QdrantVectorStore()
    dense_results = vector_store.search(
        query_vector=query_vector,
        request=dense_request,
    )

    chunks = load_chunks_from_file(request.chunks_path)

    filtered_chunks = filter_chunks(
        chunks=chunks,
        document_id=request.document_id,
        source_type=request.source_type,
        trust_level=request.trust_level,
        section=request.section,
        include_references=request.include_references,
    )

    bm25_index = BM25Index(filtered_chunks)

    bm25_results = bm25_index.search(
        query=request.question,
        top_k=request.bm25_k,
    )

    hybrid_results = reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_results=bm25_results,
        top_k=request.top_k,
    )

    prompt = build_grounded_prompt(
        question=request.question,
        contexts=hybrid_results,
    )

    generator = GroqGenerationProvider()
    answer = generator.generate(prompt)

    citations: List[Citation] = []

    for index, result in enumerate(hybrid_results, start=1):
        citations.append(
            Citation(
                citation_id=index,
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                section=result.section,
                start_page=result.start_page,
                end_page=result.end_page,
                text_preview=result.text[:240].replace("\n", " "),
            )
        )

    log_answer_event(
        request=request,
        answer=answer,
        generator_model=generator.model_name(),
        citations=citations,
        retrieved_context=hybrid_results,
    )

    return AnswerResponse(
        question=request.question,
        answer=answer,
        generator_model=generator.model_name(),
        retrieval_strategy="hybrid_dense_bm25_rrf",
        citations=citations,
        retrieved_context=hybrid_results,
    )
