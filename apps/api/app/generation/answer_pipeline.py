from typing import List

from app.chunking.loader import load_chunks_from_file
from app.dependencies import get_embedding_provider, get_generation_provider, get_vector_store
from app.generation.logger import log_answer_event
from app.generation.prompt_builder import build_grounded_prompt
from app.generation.schemas import AnswerRequest, AnswerResponse, Citation
from app.guardrails.answer_guardrails import (
    add_medical_disclaimer_if_needed,
    validate_generated_answer,
    validate_retrieved_context,
)
from app.retrieval.bm25_index import BM25Index, filter_chunks
from app.retrieval.hybrid_search import reciprocal_rank_fusion
from app.retrieval.schemas import SearchRequest


def build_citations(results) -> List[Citation]:
    citations: List[Citation] = []

    for index, result in enumerate(results, start=1):
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

    return citations


def generate_grounded_answer(request: AnswerRequest) -> AnswerResponse:
    embedding_provider = get_embedding_provider()
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

    vector_store = get_vector_store()
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

    citations = build_citations(hybrid_results)

    context_is_valid, context_guardrail_message = validate_retrieved_context(
        hybrid_results
    )

    generator = get_generation_provider()

    if not context_is_valid:
        answer = (
            "I do not have enough reliable evidence in the retrieved document context to answer this question."
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
            retrieval_strategy=f"hybrid_dense_bm25_rrf_guardrail_blocked: {context_guardrail_message}",
            citations=citations,
            retrieved_context=hybrid_results,
        )

    prompt = build_grounded_prompt(
        question=request.question,
        contexts=hybrid_results,
    )

    answer = generator.generate(prompt)
    answer = add_medical_disclaimer_if_needed(
        question=request.question,
        answer=answer,
    )

    answer_is_valid, answer_guardrail_message = validate_generated_answer(answer)

    if not answer_is_valid:
        answer = (
            "The system retrieved relevant context, but the generated answer did not pass citation or grounding checks. "
            "Please inspect the retrieved sources directly."
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
        retrieval_strategy=f"hybrid_dense_bm25_rrf_guardrail: {answer_guardrail_message}",
        citations=citations,
        retrieved_context=hybrid_results,
    )
