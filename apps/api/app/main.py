import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.ingestion.pdf_loader import load_pdf

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


@app.post("/ingest/pdf")
def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ingested_document = load_pdf(str(file_path), file.filename)
        return ingested_document
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
