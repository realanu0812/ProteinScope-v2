from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int
    text: str
    char_count: int
    is_empty: bool = False


class SectionBlock(BaseModel):
    section: Optional[str]
    text: str
    start_page: int
    end_page: int
    char_count: int


class IngestionMetrics(BaseModel):
    total_pages_in_pdf: int
    extracted_pages: int
    skipped_pages: int
    total_characters: int
    average_characters_per_page: float
    section_blocks_count: int


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    source_type: str = Field(description="e.g. scientific_paper, reddit_thread, web_article")
    trust_level: str = Field(description="e.g. verified, anecdotal, mixed")
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
    section_blocks: List[SectionBlock]


class IngestionResponse(BaseModel):
    status: str
    message: str
    output_path: Optional[str] = None
    report_path: Optional[str] = None
    document: Optional[IngestedDocument] = None
    error: Optional[str] = None
