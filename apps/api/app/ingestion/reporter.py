from pathlib import Path

from app.ingestion.schemas import IngestedDocument


def export_ingestion_report(
    document: IngestedDocument,
    output_dir: str = "outputs/ingestion"
) -> str:
    """
    Creates a readable Markdown report for ingestion inspection.

    Why:
    - JSON is too large to manually inspect every time
    - Reports help quickly validate extraction quality
    - Reports make parser/debug work easier before chunking
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    document_id = document.metadata.document_id
    output_path = Path(output_dir) / f"{document_id}_report.md"

    lines = []

    lines.append("# Ingestion Report\n")

    lines.append("## Document\n")
    lines.append(f"- Document ID: `{document.metadata.document_id}`")
    lines.append(f"- Filename: `{document.metadata.filename}`")
    lines.append(f"- Title: {document.metadata.title or 'Unknown'}")
    lines.append(f"- Author: {document.metadata.author or 'Unknown'}")
    lines.append(f"- Source Type: `{document.metadata.source_type}`")
    lines.append(f"- Trust Level: `{document.metadata.trust_level}`")
    lines.append(f"- Parser: `{document.metadata.parser_name}`")
    lines.append(f"- Parser Version: `{document.metadata.parser_version}`")
    lines.append(f"- Created At: `{document.metadata.created_at}`\n")

    lines.append("## Extraction Metrics\n")
    lines.append(f"- Total Pages in PDF: {document.metrics.total_pages_in_pdf}")
    lines.append(f"- Extracted Pages: {document.metrics.extracted_pages}")
    lines.append(f"- Skipped Pages: {document.metrics.skipped_pages}")
    lines.append(f"- Total Characters: {document.metrics.total_characters}")
    lines.append(f"- Average Characters/Page: {document.metrics.average_characters_per_page}")
    lines.append(f"- Section Blocks: {document.metrics.section_blocks_count}\n")

    lines.append("## Section Blocks\n")
    lines.append("| # | Section | Pages | Characters | Preview |")
    lines.append("|---|---|---|---:|---|")

    for index, block in enumerate(document.section_blocks, start=1):
        section = block.section or "unknown"
        pages = (
            str(block.start_page)
            if block.start_page == block.end_page
            else f"{block.start_page}-{block.end_page}"
        )
        preview = block.text[:140].replace("\n", " ").strip()
        preview = preview.replace("|", "\\|")

        lines.append(
            f"| {index} | {section} | {pages} | {block.char_count} | {preview}... |"
        )

    lines.append("\n## Page Summary\n")
    lines.append("| Page | Characters |")
    lines.append("|---:|---:|")

    for page in document.pages:
        lines.append(f"| {page.page_number} | {page.char_count} |")

    with output_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return str(output_path)
