import pymupdf # type: ignore
from pathlib import Path
from uuid import uuid4

from app.ingestion.cleaner import clean_text, is_useful_text
from app.ingestion.schemas import IngestedDocument, PageText


def load_pdf(file_path: str, filename: str) -> IngestedDocument:
    """
    Extracts page-wise text from a PDF using PyMuPDF.

    Why page-wise?
    - Enables page-level citations
    - Helps debugging extraction quality
    - Makes future chunking easier
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    document = pymupdf.open(file_path)

    pages = []

    for page_index, page in enumerate(document):
        raw_text = page.get_text("text")
        cleaned_text = clean_text(raw_text)

        if not is_useful_text(cleaned_text):
            continue

        pages.append(
            PageText(
                page_number=page_index + 1,
                text=cleaned_text
            )
        )

    metadata = document.metadata or {}

    return IngestedDocument(
        document_id=str(uuid4()),
        filename=filename,
        source_type="scientific_paper",
        trust_level="verified",
        title=metadata.get("title") or None,
        page_count=len(pages),
        pages=pages
    )
