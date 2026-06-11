from collections import Counter
from pathlib import Path
from typing import List


from app.chunking.schemas import TextChunk
from app.chunking.validator import validate_chunks

def export_chunk_report(
    document_id: str,
    chunks: List[TextChunk],
    output_dir: str = "outputs/chunks"
) -> str:
    """
    Creates a Markdown debug report for chunk inspection.

    Why:
    - Chunk JSON can be large
    - We need to inspect chunk quality before embeddings
    - Helps detect bad chunk size, bad sections, and broken text
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / f"{document_id}_chunks_report.md"

    section_counts = Counter(chunk.section or "unknown" for chunk in chunks)

    lines = []
    lines.append("# Chunking Report\n")

    lines.append("## Summary\n")
    lines.append(f"- Document ID: `{document_id}`")
    lines.append(f"- Total Chunks: {len(chunks)}")

    if chunks:
        avg_chars = round(sum(chunk.char_count for chunk in chunks) / len(chunks), 2)
        min_chars = min(chunk.char_count for chunk in chunks)
        max_chars = max(chunk.char_count for chunk in chunks)
    else:
        avg_chars = min_chars = max_chars = 0

    lines.append(f"- Average Characters/Chunk: {avg_chars}")
    lines.append(f"- Min Characters: {min_chars}")
    lines.append(f"- Max Characters: {max_chars}\n")

    validation = validate_chunks(chunks)

    lines.append("## Validation\n")
    lines.append(f"- Passed: {validation['passed']}")
    lines.append(f"- Small Chunks: {validation['small_chunks']}")
    lines.append(f"- Large Chunks: {validation['large_chunks']}")
    lines.append(f"- Missing Section Chunks: {validation['missing_section_chunks']}")
    lines.append(f"- Empty Chunks: {validation['empty_chunks']}")
    lines.append(f"- Suspicious Start Chunks: {validation['suspicious_start_chunks']}\n")

    lines.append("## Chunks by Section\n")
    lines.append("| Section | Count |")
    lines.append("|---|---:|")

    for section, count in section_counts.items():
        lines.append(f"| {section} | {count} |")

    lines.append("\n## Chunk Preview\n")
    lines.append("| Index | Section | Pages | Characters | Preview |")
    lines.append("|---:|---|---|---:|---|")

    for chunk in chunks:
        pages = (
            str(chunk.start_page)
            if chunk.start_page == chunk.end_page
            else f"{chunk.start_page}-{chunk.end_page}"
        )
        preview = chunk.text[:180].replace("\n", " ").strip()
        preview = preview.replace("|", "\\|")

        lines.append(
            f"| {chunk.chunk_index} | {chunk.section or 'unknown'} | {pages} | {chunk.char_count} | {preview}... |"
        )

    with output_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return str(output_path)
