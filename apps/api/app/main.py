import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore

from .ingestion.pdf_loader import load_pdf
from .ingestion.exporter import export_ingested_document
from .ingestion.schemas import IngestionResponse
from .ingestion.validator import validate_pdf_filename, validate_uploaded_pdf

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

        return IngestionResponse(
            status="completed",
            message="PDF ingested successfully",
            output_path=output_path,
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
