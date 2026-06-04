from pydantic import BaseModel
from typing import List, Optional


class PageText(BaseModel):
    page_number: int
    text: str


class IngestedDocument(BaseModel):
    document_id: str
    filename: str
    source_type: str
    trust_level: str
    title: Optional[str] = None
    page_count: int
    pages: List[PageText]
