import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile  # type: ignore

from app.chunking.chunker import chunk_document
from app.chunking.exporter import export_chunks
from app.chunking.loader import load_chunks_from_file
from app.chunking.reporter import export_chunk_report
from app.embeddings.exporter import create_chunk_embeddings, export_chunk_embeddings
from app.embeddings.reporter import export_embedding_report
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.ingestion.exporter import export_ingested_document
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.reporter import export_ingestion_report
from app.ingestion.schemas import IngestionResponse
from app.ingestion.validator import validate_pdf_filename, validate_uploaded_pdf
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid_search import reciprocal_rank_fusion
from app.retrieval.logger import log_search_event
from app.retrieval.schemas import (
    BM25SearchRequest,
    HybridSearchRequest,
    HybridSearchResponse,
    SearchRequest,
    SearchResponse,
)
from app.vector_store.qdrant_store import QdrantVectorStore


app = FastAPI(
    title="ProteinScope v2 API",
    description="Backend API for source-aware scientific RAG ingestion.",
    version="0.1.0",
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "ProteinScope v2 API is running",
    }


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

        ingested_document = load_pdf(
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

        embedding_provider = SentenceTransformerEmbeddingProvider()

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

        vector_store = QdrantVectorStore()
        indexed_count = vector_store.upsert_embeddings(embedded_chunks)

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
    embedding_provider = SentenceTransformerEmbeddingProvider()
    query_vector = embedding_provider.embed_texts([request.query])[0]

    vector_store = QdrantVectorStore()
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
    chunks = load_chunks_from_file(request.chunks_path)
    bm25_index = BM25Index(chunks)

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
    embedding_provider = SentenceTransformerEmbeddingProvider()
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

    vector_store = QdrantVectorStore()
    dense_results = vector_store.search(
        query_vector=query_vector,
        request=dense_request,
    )

    chunks = load_chunks_from_file(request.chunks_path)
    bm25_index = BM25Index(chunks)
    bm25_results = bm25_index.search(
        query=request.query,
        top_k=request.bm25_k,
    )

    hybrid_results = reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_results=bm25_results,
        top_k=request.top_k,
    )

    return HybridSearchResponse(
        query=request.query,
        top_k=request.top_k,
        dense_k=request.dense_k,
        bm25_k=request.bm25_k,
        results=hybrid_results,
    )
