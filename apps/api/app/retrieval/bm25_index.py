import re
from typing import List, Optional

from rank_bm25 import BM25Okapi

from app.chunking.schemas import TextChunk
from app.retrieval.schemas import SearchResult


def tokenize(text: str) -> List[str]:
    """
    Simple tokenizer for BM25.

    Keeps biomedical/scientific terms reasonably intact:
    - IL-6
    - TP53
    - mTOR
    - p-value
    """

    return re.findall(r"[a-zA-Z0-9α-ωΑ-Ω\-]+", text.lower())


def filter_chunks(
    chunks: List[TextChunk],
    document_id: Optional[str] = None,
    source_type: Optional[str] = None,
    trust_level: Optional[str] = None,
    section: Optional[str] = None,
    include_references: bool = False,
) -> List[TextChunk]:
    """
    Applies metadata filters before building/searching BM25.

    This keeps BM25 behavior aligned with dense retrieval filters.
    """

    filtered_chunks = []

    for chunk in chunks:
        if document_id and chunk.document_id != document_id:
            continue

        if source_type and chunk.source_type != source_type:
            continue

        if trust_level and chunk.trust_level != trust_level:
            continue

        if section and chunk.section != section:
            continue

        if not include_references and chunk.section == "references":
            continue

        filtered_chunks.append(chunk)

    return filtered_chunks


class BM25Index:
    def __init__(self, chunks: List[TextChunk]):
        self.chunks = chunks
        self.tokenized_chunks = [tokenize(chunk.text) for chunk in chunks]
        self.index = BM25Okapi(self.tokenized_chunks) if chunks else None

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not self.chunks or self.index is None:
            return []

        tokenized_query = tokenize(query)
        scores = self.index.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            chunk = self.chunks[index]
            score = float(scores[index])

            if score <= 0:
                continue

            results.append(
                SearchResult(
                    score=score,
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    source_type=chunk.source_type,
                    trust_level=chunk.trust_level,
                    section=chunk.section,
                    start_page=chunk.start_page,
                    end_page=chunk.end_page,
                    text=chunk.text,
                )
            )

        return results
