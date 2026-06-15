import json
from pathlib import Path
from typing import List

from app.chunking.schemas import TextChunk


def load_chunks_from_file(file_path: str) -> List[TextChunk]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Chunks file not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        raw_chunks = json.load(file)

    return [TextChunk(**chunk) for chunk in raw_chunks]
