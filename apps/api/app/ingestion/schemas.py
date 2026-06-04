from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int
    text: str
    char_count: int
    is_empty: bool = False


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
    pages: List[PageText]
