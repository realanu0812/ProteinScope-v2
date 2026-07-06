from functools import lru_cache
from typing import Optional

from app.chunking.loader import load_chunks_from_file
from app.retrieval.bm25_index import BM25Index, filter_chunks


@lru_cache(maxsize=32)
def get_cached_bm25_index(
    chunks_path: str,
    document_id: Optional[str] = None,
    source_type: Optional[str] = None,
    trust_level: Optional[str] = None,
    section: Optional[str] = None,
    include_references: bool = False,
) -> BM25Index:
    chunks = load_chunks_from_file(chunks_path)

    filtered_chunks = filter_chunks(
        chunks=chunks,
        document_id=document_id,
        source_type=source_type,
        trust_level=trust_level,
        section=section,
        include_references=include_references,
    )

    return BM25Index(filtered_chunks)
