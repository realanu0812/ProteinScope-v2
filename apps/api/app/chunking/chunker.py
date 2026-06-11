from typing import List
from uuid import uuid4

from app.ingestion.schemas import IngestedDocument, SectionBlock
from app.chunking.schemas import TextChunk


TARGET_CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def split_text_with_overlap(
    text: str,
    target_size: int = TARGET_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Character-based baseline splitter.

    Later we will upgrade this to token-aware splitting.
    """

    text = text.strip()

    if len(text) <= target_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + target_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(text):
            break

    return chunks


def chunk_section_block(
    document: IngestedDocument,
    section_block: SectionBlock,
    starting_index: int
) -> List[TextChunk]:
    """
    Converts one section block into one or more chunks.
    """

    pieces = split_text_with_overlap(section_block.text)
    chunks = []

    for offset, piece in enumerate(pieces):
        chunk_index = starting_index + offset

        chunks.append(
            TextChunk(
                chunk_id=str(uuid4()),
                document_id=document.metadata.document_id,
                source_type=document.metadata.source_type,
                trust_level=document.metadata.trust_level,
                section=section_block.section,
                start_page=section_block.start_page,
                end_page=section_block.end_page,
                chunk_index=chunk_index,
                text=piece,
                char_count=len(piece),
            )
        )

    return chunks


def chunk_document(document: IngestedDocument) -> List[TextChunk]:
    """
    Creates retrieval-ready chunks from section blocks.

    We chunk section_blocks instead of pages because section_blocks preserve
    scientific document structure better.
    """

    all_chunks: List[TextChunk] = []
    current_index = 0

    for section_block in document.section_blocks:
        block_chunks = chunk_section_block(
            document=document,
            section_block=section_block,
            starting_index=current_index,
        )

        all_chunks.extend(block_chunks)
        current_index += len(block_chunks)

    return all_chunks
