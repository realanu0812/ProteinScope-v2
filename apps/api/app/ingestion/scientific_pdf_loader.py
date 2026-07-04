from app.ingestion.grobid_client import GrobidClient
from app.ingestion.grobid_parser import parse_grobid_tei
from app.ingestion.pdf_loader import load_pdf


def load_scientific_pdf(file_path: str, filename: str, document_id: str):
    """
    Production-style scientific PDF loader.

    Strategy:
    1. Use PyMuPDF for page-wise extraction and citation-friendly pages.
    2. Use GROBID for scholarly section extraction.
    3. Fall back to PyMuPDF section blocks if GROBID fails.
    """

    document = load_pdf(
        file_path=file_path,
        filename=filename,
        document_id=document_id,
    )

    grobid_client = GrobidClient()

    if not grobid_client.is_alive():
        document.metadata.parser_name = "pymupdf"
        return document

    try:
        tei_xml = grobid_client.process_fulltext_document(file_path)
        title, author, section_blocks = parse_grobid_tei(
            tei_xml=tei_xml,
            pages=document.pages,
        )

        if section_blocks:
            document.section_blocks = section_blocks
            document.metrics.section_blocks_count = len(section_blocks)
            document.metadata.parser_name = "pymupdf+grobid"

            if title:
                document.metadata.title = title

            if author:
                document.metadata.author = author

        return document

    except Exception:
        document.metadata.parser_name = "pymupdf_fallback"
        return document
