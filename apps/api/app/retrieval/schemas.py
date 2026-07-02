from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = 5
    document_id: Optional[str] = None
    source_type: Optional[str] = None
    trust_level: Optional[str] = None
    section: Optional[str] = None
    include_references: bool = False


class BM25SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    chunks_path: str
    top_k: int = 5


class HybridSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    chunks_path: str
    top_k: int = 5
    dense_k: int = 20
    bm25_k: int = 20
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


class HybridSearchResult(SearchResult):
    dense_rank: Optional[int] = None
    bm25_rank: Optional[int] = None
    fusion_score: float


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResult]


class HybridSearchResponse(BaseModel):
    query: str
    top_k: int
    dense_k: int
    bm25_k: int
    results: List[HybridSearchResult]
