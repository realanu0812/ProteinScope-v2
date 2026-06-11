from typing import List, Optional

from pydantic import BaseModel


class ChunkEmbedding(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    source_type: str
    trust_level: str
    section: Optional[str]
    start_page: int
    end_page: int
    text: str
    embedding_model: str
    embedding: List[float]
