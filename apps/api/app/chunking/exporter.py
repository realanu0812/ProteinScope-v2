import json
from pathlib import Path
from typing import List

from app.chunking.schemas import TextChunk


def export_chunks(
    document_id: str,
    chunks: List[TextChunk],
    output_dir: str = "outputs/chunks"
) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / f"{document_id}_chunks.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            [chunk.model_dump() for chunk in chunks],
            file,
            indent=2,
            ensure_ascii=False
        )

    return str(output_path)
