from pathlib import Path

import pymupdf # type: ignore


MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def validate_pdf_filename(filename: str) -> None:
    if not filename:
        raise ValueError("Missing filename.")

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported currently.")


def validate_file_size(file_path: Path) -> None:
    if not file_path.exists():
        raise ValueError("Uploaded file was not saved correctly.")

    file_size = file_path.stat().st_size

    if file_size == 0:
        raise ValueError("Uploaded file is empty.")

    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File too large. Max allowed size is {MAX_FILE_SIZE_MB} MB.")


def validate_pdf_can_open(file_path: Path) -> None:
    try:
        document = pymupdf.open(file_path)
        page_count = len(document)

        if page_count == 0:
            raise ValueError("PDF has no pages.")

        document.close()

    except Exception as error:
        raise ValueError(f"Invalid or corrupted PDF: {error}")


def validate_uploaded_pdf(file_path: Path, filename: str) -> None:
    validate_pdf_filename(filename)
    validate_file_size(file_path)
    validate_pdf_can_open(file_path)
