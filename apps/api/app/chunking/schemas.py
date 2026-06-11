from typing import Optional

from pydantic import BaseModel


class TextChunk(BaseModel):
    chunk_id: str
    document_id: str
    source_type: str
    trust_level: str
    section: Optional[str]
    start_page: int
    end_page: int
    chunk_index: int
    text: str
    char_count: int
