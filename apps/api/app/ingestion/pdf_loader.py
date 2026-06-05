import fitz
from pathlib import Path
from typing import Optional

from app.ingestion.cleaner import clean_text, is_useful_text
from app.ingestion.section_detector import detect_section_from_text
from app.ingestion.schemas import (
    IngestedDocument,
    PageText,
    DocumentMetadata,
    IngestionMetrics,
)


def load_pdf(file_path: str, filename: str, document_id: str) -> IngestedDocument:
    """
    Extracts page-wise text from a PDF using PyMuPDF.

    We also attach basic section labels to pages when possible.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    document = fitz.open(file_path)
    raw_metadata = document.metadata or {}

    total_pages_in_pdf = len(document)
    pages = []

    current_section: Optional[str] = None

    for page_index, page in enumerate(document):
        raw_text = page.get_text("text")
        cleaned_text = clean_text(raw_text)
        useful = is_useful_text(cleaned_text)

        if not useful:
            continue

        detected_section = detect_section_from_text(cleaned_text)

        if detected_section:
            current_section = detected_section

        pages.append(
            PageText(
                page_number=page_index + 1,
                text=cleaned_text,
                char_count=len(cleaned_text),
                section=current_section,
                is_empty=False
            )
        )

    total_characters = sum(page.char_count for page in pages)
    extracted_pages = len(pages)
    skipped_pages = total_pages_in_pdf - extracted_pages

    average_characters_per_page = (
        total_characters / extracted_pages if extracted_pages > 0 else 0
    )

    metadata = DocumentMetadata(
        document_id=document_id,
        filename=filename,
        source_type="scientific_paper",
        trust_level="verified",
        title=raw_metadata.get("title") or None,
        author=raw_metadata.get("author") or None,
        parser_name="pymupdf",
        parser_version=fitz.version[0],
        ingestion_status="completed"
    )

    metrics = IngestionMetrics(
        total_pages_in_pdf=total_pages_in_pdf,
        extracted_pages=extracted_pages,
        skipped_pages=skipped_pages,
        total_characters=total_characters,
        average_characters_per_page=round(average_characters_per_page, 2),
    )

    return IngestedDocument(
        metadata=metadata,
        page_count=extracted_pages,
        metrics=metrics,
        pages=pages
    )
