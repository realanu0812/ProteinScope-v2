import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


REGISTRY_PATH = Path("outputs/documents/document_registry.json")


class DocumentRecord(BaseModel):
    document_id: str
    title: Optional[str] = None
    filename: Optional[str] = None
    chunks_path: str
    chunk_count: int
    embedding_count: int
    indexed_count: int
    parser_name: Optional[str] = None
    created_at: str


def load_document_registry() -> List[DocumentRecord]:
    if not REGISTRY_PATH.exists():
        return []

    with REGISTRY_PATH.open("r", encoding="utf-8") as file:
        raw_records = json.load(file)

    return [DocumentRecord(**record) for record in raw_records]


def save_document_registry(records: List[DocumentRecord]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REGISTRY_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            [record.model_dump() for record in records],
            file,
            indent=2,
            ensure_ascii=False,
        )


def upsert_document_record(record: DocumentRecord) -> DocumentRecord:
    records = load_document_registry()

    filtered_records = [
        existing
        for existing in records
        if existing.document_id != record.document_id
    ]

    filtered_records.append(record)
    save_document_registry(filtered_records)

    return record


def get_document_record(document_id: str) -> Optional[DocumentRecord]:
    records = load_document_registry()

    for record in records:
        if record.document_id == document_id:
            return record

    return None


def build_document_record(
    document_id: str,
    title: Optional[str],
    filename: Optional[str],
    chunks_path: str,
    chunk_count: int,
    embedding_count: int,
    indexed_count: int,
    parser_name: Optional[str],
) -> DocumentRecord:
    return DocumentRecord(
        document_id=document_id,
        title=title,
        filename=filename,
        chunks_path=chunks_path,
        chunk_count=chunk_count,
        embedding_count=embedding_count,
        indexed_count=indexed_count,
        parser_name=parser_name,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
