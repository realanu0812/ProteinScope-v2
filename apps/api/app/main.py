import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.exporter import export_ingested_document
from app.ingestion.reporter import export_ingestion_report
from app.ingestion.schemas import IngestionResponse
from app.ingestion.validator import validate_pdf_filename, validate_uploaded_pdf

from app.chunking.chunker import chunk_document
from app.chunking.exporter import export_chunks
from app.chunking.reporter import export_chunk_report

from app.embeddings.exporter import create_chunk_embeddings, export_chunk_embeddings
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.embeddings.reporter import export_embedding_report

from app.vector_store.qdrant_store import QdrantVectorStore

app = FastAPI(
    title="ProteinScope v2 API",
    description="Backend API for source-aware scientific RAG ingestion.",
    version="0.1.0"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "ProteinScope v2 API is running"
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
            document_id=document_id
        )

        if ingested_document.page_count == 0:
            return IngestionResponse(
                status="failed",
                message="PDF ingestion failed",
                error="No useful text was extracted. This may be a scanned PDF and may require OCR."
            )

        output_path = export_ingested_document(ingested_document)
        report_path = export_ingestion_report(ingested_document)

        chunks = chunk_document(ingested_document)
        chunks_path = export_chunks(
            document_id=ingested_document.metadata.document_id,
            chunks=chunks
        )
        chunks_report_path = export_chunk_report(
            document_id=ingested_document.metadata.document_id,
            chunks=chunks
        )

        embedding_provider = SentenceTransformerEmbeddingProvider()
        embedded_chunks = create_chunk_embeddings(
            chunks=chunks,
            provider=embedding_provider
        )
        embeddings_path = export_chunk_embeddings(
            document_id=ingested_document.metadata.document_id,
            embeddings=embedded_chunks
        )
        embeddings_report_path = export_embedding_report(
            document_id=ingested_document.metadata.document_id,
            embeddings=embedded_chunks
        )
        vector_store = QdrantVectorStore()
        indexed_count = vector_store.upsert_embeddings(embedded_chunks)

        return IngestionResponse(
            status="completed",
            message="PDF ingested, chunked, and embedded successfully",
            output_path=output_path,
            report_path=report_path,
            chunks_path=chunks_path,
            chunks_report_path=chunks_report_path,
            chunk_count=len(chunks),
            embeddings_path=embeddings_path,
            embedding_count=len(embedded_chunks),
            embedding_model=embedding_provider.model_name(),
            embeddings_report_path=embeddings_report_path,
            indexed_count=indexed_count,
            document=ingested_document
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        return IngestionResponse(
            status="failed",
            message="PDF ingestion failed",
            error=str(error)
        )
