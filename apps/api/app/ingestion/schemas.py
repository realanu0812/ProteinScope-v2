from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int
    text: str
    char_count: int
    is_empty: bool = False


class IngestionMetrics(BaseModel):
    total_pages_in_pdf: int
    extracted_pages: int
    skipped_pages: int
    total_characters: int
    average_characters_per_page: float


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str

    source_type: str = Field(
        description="Type of source, e.g. scientific_paper, reddit_thread, web_article"
    )
    trust_level: str = Field(
        description="Trust level of source, e.g. verified, anecdotal, mixed"
    )

    title: Optional[str] = None
    author: Optional[str] = None

    parser_name: str
    parser_version: str

    ingestion_status: str = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IngestedDocument(BaseModel):
    metadata: DocumentMetadata
    page_count: int
    metrics: IngestionMetrics
    pages: List[PageText]


class IngestionResponse(BaseModel):
    status: str
    message: str
    output_path: Optional[str] = None
    document: Optional[IngestedDocument] = None
    error: Optional[str] = None
