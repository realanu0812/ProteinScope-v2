import json
from pathlib import Path
from app.ingestion.schemas import IngestedDocument


def export_ingested_document(document: IngestedDocument, output_dir: str = "outputs/ingestion") -> str:
    """
    Saves ingested document output as JSON for debugging.
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / f"{document.metadata.document_id}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(document.model_dump(mode="json"), file, indent=2, ensure_ascii=False)

    return str(output_path)
