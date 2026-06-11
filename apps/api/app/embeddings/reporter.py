from pathlib import Path
from typing import List

from app.embeddings.schemas import ChunkEmbedding


def export_embedding_report(
    document_id: str,
    embeddings: List[ChunkEmbedding],
    output_dir: str = "outputs/embeddings"
) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / f"{document_id}_embeddings_report.md"

    lines = []
    lines.append("# Embedding Report\n")

    lines.append("## Summary\n")
    lines.append(f"- Document ID: `{document_id}`")
    lines.append(f"- Embedding Count: {len(embeddings)}")

    if embeddings:
        model_name = embeddings[0].embedding_model
        dimension = len(embeddings[0].embedding)
    else:
        model_name = "unknown"
        dimension = 0

    lines.append(f"- Embedding Model: `{model_name}`")
    lines.append(f"- Vector Dimension: {dimension}\n")

    lines.append("## Embedded Chunk Preview\n")
    lines.append("| Chunk Index | Section | Pages | Vector Dim | Text Preview |")
    lines.append("|---:|---|---|---:|---|")

    for item in embeddings[:30]:
        pages = (
            str(item.start_page)
            if item.start_page == item.end_page
            else f"{item.start_page}-{item.end_page}"
        )
        preview = item.text[:160].replace("\n", " ").strip()
        preview = preview.replace("|", "\\|")

        lines.append(
            f"| {item.chunk_index} | {item.section or 'unknown'} | {pages} | {len(item.embedding)} | {preview}... |"
        )

    if len(embeddings) > 30:
        lines.append(f"\nShowing first 30 of {len(embeddings)} embeddings.")

    with output_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return str(output_path)
