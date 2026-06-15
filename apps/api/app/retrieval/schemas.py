from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = 5


class SearchResult(BaseModel):
    score: float
    chunk_id: str
    document_id: str
    chunk_index: int
    source_type: str
    trust_level: str
    section: Optional[str] = None
    start_page: int
    end_page: int
    text: str


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResult]
