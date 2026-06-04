import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.exporter import export_ingested_document
from app.ingestion.schemas import IngestionResponse

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
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")

    file_path = UPLOAD_DIR / file.filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ingested_document = load_pdf(str(file_path), file.filename)
        output_path = export_ingested_document(ingested_document)

        return IngestionResponse(
            status="completed",
            message="PDF ingested successfully",
            output_path=output_path,
            document=ingested_document
        )

    except Exception as error:
        return IngestionResponse(
            status="failed",
            message="PDF ingestion failed",
            error=str(error)
        )
