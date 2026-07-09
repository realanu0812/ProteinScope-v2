from typing import List, Optional

from pydantic import BaseModel, Field

from app.retrieval.schemas import HybridSearchResult


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1)
    chunks_path: str
    top_k: int = 5
    dense_k: int = 30
    bm25_k: int = 30
    document_id: Optional[str] = None
    source_type: Optional[str] = None
    trust_level: Optional[str] = None
    section: Optional[str] = None
    include_references: bool = False
    include_community_discussion: bool = True


class Citation(BaseModel):
    citation_id: int
    chunk_id: str
    document_id: str
    section: Optional[str]
    start_page: int
    end_page: int
    text_preview: str


class CommunityDiscussionItem(BaseModel):
    source_id: int
    platform: str = "reddit"
    subreddit: Optional[str] = None
    thread_title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    text_preview: str
    trust_level: str = "community"


class AnswerResponse(BaseModel):
    question: str
    answer: str
    generator_model: str
    retrieval_strategy: str
    citations: List[Citation]
    community_discussion: List[CommunityDiscussionItem]
    retrieved_context: List[HybridSearchResult]
