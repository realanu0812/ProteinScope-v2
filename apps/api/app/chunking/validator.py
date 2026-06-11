from typing import Dict, List

from app.chunking.schemas import TextChunk


MIN_CHUNK_CHARS = 120
MAX_CHUNK_CHARS = 1400


def validate_chunks(chunks: List[TextChunk]) -> Dict:
    total_chunks = len(chunks)

    small_chunks = [
        chunk.chunk_index for chunk in chunks
        if chunk.char_count < MIN_CHUNK_CHARS
    ]

    large_chunks = [
        chunk.chunk_index for chunk in chunks
        if chunk.char_count > MAX_CHUNK_CHARS
    ]

    missing_section_chunks = [
        chunk.chunk_index for chunk in chunks
        if chunk.section is None
    ]

    empty_chunks = [
        chunk.chunk_index for chunk in chunks
        if not chunk.text.strip()
    ]

    suspicious_start_chunks = [
        chunk.chunk_index for chunk in chunks
        if chunk.text and chunk.text[0].islower()
    ]

    return {
        "total_chunks": total_chunks,
        "small_chunks": small_chunks,
        "large_chunks": large_chunks,
        "missing_section_chunks": missing_section_chunks,
        "empty_chunks": empty_chunks,
        "suspicious_start_chunks": suspicious_start_chunks,
        "passed": len(empty_chunks) == 0
    }
