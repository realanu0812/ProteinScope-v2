import re
from typing import List

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


class BM25Index:
    def __init__(self, chunks: List[TextChunk]):
        self.chunks = chunks
        self.tokenized_chunks = [tokenize(chunk.text) for chunk in chunks]
        self.index = BM25Okapi(self.tokenized_chunks)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
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
