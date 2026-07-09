from typing import List, Optional

from pydantic import BaseModel, Field


class CommunitySourceInput(BaseModel):
    query: str = Field(min_length=1)
    platform: str = "reddit"
    subreddit: Optional[str] = None
    thread_title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    text: str = Field(min_length=1)


class CommunityIngestRequest(BaseModel):
    document_id: Optional[str] = None
    topic: str = Field(min_length=1)
    sources: List[CommunitySourceInput]


class CommunitySourceRecord(BaseModel):
    community_id: str
    document_id: Optional[str] = None
    topic: str
    query: str
    platform: str
    subreddit: Optional[str] = None
    thread_title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    text: str
    source_type: str = "community_discussion"
    trust_level: str = "community"


class CommunityIngestResponse(BaseModel):
    status: str
    message: str
    topic: str
    document_id: Optional[str] = None
    source_count: int
    output_path: str
    sources: List[CommunitySourceRecord]
