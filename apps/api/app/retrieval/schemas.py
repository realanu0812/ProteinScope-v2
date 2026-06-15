from typing import List, Optional

from pydantic import BaseModel, Field # type: ignore



class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = 5
    document_id: Optional[str] = None
    source_type: Optional[str] = None
    trust_level: Optional[str] = None
    section: Optional[str] = None
    include_references: bool = False


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
