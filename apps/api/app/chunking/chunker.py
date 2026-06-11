import re
from typing import List
from uuid import uuid4

from app.ingestion.schemas import IngestedDocument, SectionBlock
from app.chunking.schemas import TextChunk


TARGET_CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def split_large_text_with_overlap(
    text: str,
    target_size: int = TARGET_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Fallback splitter for very large text pieces.
    Used only when paragraph/sentence splitting is not enough.
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

        if start >= len(text):
            break

    return chunks


def split_into_sentences(text: str) -> List[str]:
    """
    Basic sentence splitter.

    Conservative approach:
    - handles common sentence endings
    - not perfect for scientific abbreviations
    - good enough as a baseline before NLP-based splitting
    """

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def split_into_paragraphs(text: str) -> List[str]:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def add_overlap(previous_chunk: str, current_text: str, overlap: int = CHUNK_OVERLAP) -> str:
    """
    Adds trailing context from previous chunk to current chunk.
    """

    if not previous_chunk:
        return current_text

    overlap_text = previous_chunk[-overlap:].strip()

    if not overlap_text:
        return current_text

    return f"{overlap_text}\n{current_text}".strip()


def recursive_split_text(text: str, target_size: int = TARGET_CHUNK_SIZE) -> List[str]:
    """
    Recursive-ish baseline splitter:
    1. Preserve paragraphs when possible
    2. Split large paragraphs into sentences
    3. Split oversized sentences by characters
    """

    paragraphs = split_into_paragraphs(text)

    raw_chunks: List[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(paragraph) > target_size:
            if current_chunk:
                raw_chunks.append(current_chunk.strip())
                current_chunk = ""

            sentences = split_into_sentences(paragraph)
            sentence_buffer = ""

            for sentence in sentences:
                if len(sentence) > target_size:
                    if sentence_buffer:
                        raw_chunks.append(sentence_buffer.strip())
                        sentence_buffer = ""

                    raw_chunks.extend(split_large_text_with_overlap(sentence))
                    continue

                candidate = f"{sentence_buffer} {sentence}".strip()

                if len(candidate) <= target_size:
                    sentence_buffer = candidate
                else:
                    if sentence_buffer:
                        raw_chunks.append(sentence_buffer.strip())
                    sentence_buffer = sentence

            if sentence_buffer:
                raw_chunks.append(sentence_buffer.strip())

            continue

        candidate = f"{current_chunk}\n\n{paragraph}".strip()

        if len(candidate) <= target_size:
            current_chunk = candidate
        else:
            if current_chunk:
                raw_chunks.append(current_chunk.strip())
            current_chunk = paragraph

    if current_chunk:
        raw_chunks.append(current_chunk.strip())

    chunks_with_overlap = []

    for index, chunk in enumerate(raw_chunks):
        if index == 0:
            chunks_with_overlap.append(chunk)
        else:
            chunks_with_overlap.append(add_overlap(raw_chunks[index - 1], chunk))

    return chunks_with_overlap


def chunk_section_block(
    document: IngestedDocument,
    section_block: SectionBlock,
    starting_index: int
) -> List[TextChunk]:
    pieces = recursive_split_text(section_block.text)
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
