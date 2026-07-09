import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile  # type: ignore
from fastapi.middleware.cors import CORSMiddleware

from app.chunking.chunker import chunk_document
from app.chunking.exporter import export_chunks
from app.chunking.reporter import export_chunk_report
from app.dependencies import get_embedding_provider, get_reranker, get_vector_store
from app.documents.registry import (
    build_document_record,
    get_document_record,
    load_document_registry,
    upsert_document_record,
)
from app.embeddings.exporter import create_chunk_embeddings, export_chunk_embeddings
from app.embeddings.reporter import export_embedding_report
from app.generation.answer_pipeline import generate_grounded_answer
from app.generation.schemas import AnswerRequest, AnswerResponse
from app.health.checks import run_health_checks
from app.ingestion.exporter import export_ingested_document
from app.ingestion.reporter import export_ingestion_report
from app.ingestion.schemas import IngestionResponse
from app.ingestion.scientific_pdf_loader import load_scientific_pdf
from app.ingestion.validator import validate_pdf_filename, validate_uploaded_pdf
from app.observability.latency_logger import LatencyLoggingMiddleware
from app.retrieval.bm25_cache import get_cached_bm25_index
from app.retrieval.hybrid_search import reciprocal_rank_fusion
from app.retrieval.logger import log_hybrid_search_event, log_search_event
from app.retrieval.schemas import (
    BM25SearchRequest,
    HybridSearchRequest,
    HybridSearchResponse,
    RerankSearchRequest,
    RerankSearchResponse,
    SearchRequest,
    SearchResponse,
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.38:3000",
]


app = FastAPI(
    title="ProteinScope v2 API",
    description="Backend API for source-aware scientific RAG ingestion.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LatencyLoggingMiddleware)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "ProteinScope v2 API is running",
    }


@app.get("/health")
def detailed_health_check():
    return run_health_checks()


@app.get("/documents")
def list_documents():
    return {
        "documents": load_document_registry(),
    }


@app.get("/documents/{document_id}")
def get_document(document_id: str):
    record = get_document_record(document_id)

    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    return record


@app.post("/ingest/pdf", response_model=IngestionResponse)
def ingest_pdf(file: UploadFile = File(...)):
    try:
        validate_pdf_filename(file.filename)

        document_id = str(uuid4())
        document_dir = UPLOAD_DIR / document_id
        document_dir.mkdir(parents=True, exist_ok=True)

        raw_file_path = document_dir / "original.pdf"

        with raw_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        validate_uploaded_pdf(raw_file_path, file.filename)

        ingested_document = load_scientific_pdf(
            file_path=str(raw_file_path),
            filename=file.filename,
            document_id=document_id,
        )

        if ingested_document.page_count == 0:
            return IngestionResponse(
                status="failed",
                message="PDF ingestion failed",
                error="No useful text was extracted. This may be a scanned PDF and may require OCR.",
            )

        output_path = export_ingested_document(ingested_document)
        report_path = export_ingestion_report(ingested_document)

        chunks = chunk_document(ingested_document)

        chunks_path = export_chunks(
            document_id=ingested_document.metadata.document_id,
            chunks=chunks,
        )

        chunks_report_path = export_chunk_report(
            document_id=ingested_document.metadata.document_id,
            chunks=chunks,
        )

        embedding_provider = get_embedding_provider()

        embedded_chunks = create_chunk_embeddings(
            chunks=chunks,
            provider=embedding_provider,
        )

        embeddings_path = export_chunk_embeddings(
            document_id=ingested_document.metadata.document_id,
            embeddings=embedded_chunks,
        )

        embeddings_report_path = export_embedding_report(
            document_id=ingested_document.metadata.document_id,
            embeddings=embedded_chunks,
        )

        vector_store = get_vector_store()
        indexed_count = vector_store.upsert_embeddings(embedded_chunks)

        upsert_document_record(
            build_document_record(
                document_id=ingested_document.metadata.document_id,
                title=ingested_document.metadata.title,
                filename=file.filename,
                chunks_path=chunks_path,
                chunk_count=len(chunks),
                embedding_count=len(embedded_chunks),
                indexed_count=indexed_count,
                parser_name=ingested_document.metadata.parser_name,
            )
        )

        return IngestionResponse(
            status="completed",
            message="PDF ingested, chunked, embedded, and indexed successfully",
            output_path=output_path,
            report_path=report_path,
            chunks_path=chunks_path,
            chunks_report_path=chunks_report_path,
            chunk_count=len(chunks),
            embeddings_path=embeddings_path,
            embeddings_report_path=embeddings_report_path,
            embedding_count=len(embedded_chunks),
            embedding_model=embedding_provider.model_name(),
            indexed_count=indexed_count,
            document=ingested_document,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        return IngestionResponse(
            status="failed",
            message="PDF ingestion failed",
            error=str(error),
        )


@app.post("/search", response_model=SearchResponse)
def search_chunks(request: SearchRequest):
    embedding_provider = get_embedding_provider()
    query_vector = embedding_provider.embed_texts([request.query])[0]

    vector_store = get_vector_store()
    results = vector_store.search(
        query_vector=query_vector,
        request=request,
    )

    log_search_event(
        request=request,
        results=results,
    )

    return SearchResponse(
        query=request.query,
        top_k=request.top_k,
        results=results,
    )


@app.post("/search/bm25", response_model=SearchResponse)
def search_chunks_bm25(request: BM25SearchRequest):
    bm25_index = get_cached_bm25_index(
        chunks_path=request.chunks_path,
        include_references=False,
    )

    results = bm25_index.search(
        query=request.query,
        top_k=request.top_k,
    )

    return SearchResponse(
        query=request.query,
        top_k=request.top_k,
        results=results,
    )


@app.post("/search/hybrid", response_model=HybridSearchResponse)
def search_chunks_hybrid(request: HybridSearchRequest):
    embedding_provider = get_embedding_provider()
    query_vector = embedding_provider.embed_texts([request.query])[0]

    dense_request = SearchRequest(
        query=request.query,
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

    bm25_index = get_cached_bm25_index(
        chunks_path=request.chunks_path,
        document_id=request.document_id,
        source_type=request.source_type,
        trust_level=request.trust_level,
        section=request.section,
        include_references=request.include_references,
    )

    bm25_results = bm25_index.search(
        query=request.query,
        top_k=request.bm25_k,
    )

    hybrid_results = reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_results=bm25_results,
        top_k=request.top_k,
    )

    log_hybrid_search_event(
        request=request,
        dense_results=dense_results,
        bm25_results=bm25_results,
        hybrid_results=hybrid_results,
    )

    return HybridSearchResponse(
        query=request.query,
        top_k=request.top_k,
        dense_k=request.dense_k,
        bm25_k=request.bm25_k,
        results=hybrid_results,
    )


@app.post("/search/rerank", response_model=RerankSearchResponse)
def search_chunks_rerank(request: RerankSearchRequest):
    hybrid_request = HybridSearchRequest(
        query=request.query,
        chunks_path=request.chunks_path,
        top_k=request.candidate_k,
        dense_k=request.dense_k,
        bm25_k=request.bm25_k,
        document_id=request.document_id,
        source_type=request.source_type,
        trust_level=request.trust_level,
        section=request.section,
        include_references=request.include_references,
    )

    embedding_provider = get_embedding_provider()
    query_vector = embedding_provider.embed_texts([request.query])[0]

    dense_request = SearchRequest(
        query=request.query,
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

    bm25_index = get_cached_bm25_index(
        chunks_path=request.chunks_path,
        document_id=request.document_id,
        source_type=request.source_type,
        trust_level=request.trust_level,
        section=request.section,
        include_references=request.include_references,
    )

    bm25_results = bm25_index.search(
        query=request.query,
        top_k=request.bm25_k,
    )

    hybrid_candidates = reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_results=bm25_results,
        top_k=request.candidate_k,
    )

    reranker = get_reranker()

    reranked_results = reranker.rerank(
        query=request.query,
        results=hybrid_candidates,
        top_k=request.rerank_top_k,
    )

    log_hybrid_search_event(
        request=hybrid_request,
        dense_results=dense_results,
        bm25_results=bm25_results,
        hybrid_results=hybrid_candidates,
    )

    return RerankSearchResponse(
        query=request.query,
        candidate_k=request.candidate_k,
        rerank_top_k=request.rerank_top_k,
        reranker_model=reranker.model_name(),
        results=reranked_results,
    )


@app.post("/answer", response_model=AnswerResponse)
def answer_question(request: AnswerRequest):
    return generate_grounded_answer(request)
