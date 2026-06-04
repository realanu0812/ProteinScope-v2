import json
from pathlib import Path
from .schemas import IngestedDocument


def export_ingested_document(document: IngestedDocument, output_dir: str = "outputs/ingestion") -> str:
    """
    Saves ingested document output as JSON for debugging.

    Why this matters:
    - Lets us inspect parser quality
    - Helps identify broken text, headers, footers, empty pages
    - Prevents embedding bad extracted text
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / f"{document.document_id}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(document.model_dump(), file, indent=2, ensure_ascii=False)

    return str(output_path)
