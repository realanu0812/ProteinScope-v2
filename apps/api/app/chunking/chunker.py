import re
from typing import List
from uuid import uuid4

from app.ingestion.schemas import IngestedDocument, SectionBlock
from app.chunking.schemas import TextChunk


TARGET_CHUNK_SIZE = 900
CHUNK_OVERLAP_SENTENCES = 1


def split_into_paragraphs(text: str) -> List[str]:
    """
    Splits text into paragraphs using blank lines.
    """

    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def split_into_sentences(text: str) -> List[str]:
    """
    Baseline sentence splitter.

    This avoids character-based overlap so chunks do not start mid-word.
    It is still a baseline and may be improved later with an NLP/tokenizer-based splitter.
    """

    # Normalize internal whitespace but preserve readable sentence boundaries.
    text = re.sub(r"\s+", " ", text.strip())

    # Split on sentence-ending punctuation followed by whitespace and likely next sentence start.
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def split_oversized_sentence(sentence: str, target_size: int = TARGET_CHUNK_SIZE) -> List[str]:
    """
    Fallback for rare oversized sentences.

    Instead of cutting blindly at exactly target_size, split on word boundaries.
    """

    words = sentence.split()
    chunks: List[str] = []
    current_words: List[str] = []

    for word in words:
        candidate = " ".join(current_words + [word]).strip()

        if len(candidate) <= target_size:
            current_words.append(word)
        else:
            if current_words:
                chunks.append(" ".join(current_words).strip())
            current_words = [word]

    if current_words:
        chunks.append(" ".join(current_words).strip())

    return chunks


def recursive_split_text(text: str, target_size: int = TARGET_CHUNK_SIZE) -> List[str]:
    """
    Section-aware recursive splitter.

    Priority:
    1. Preserve paragraphs
    2. Preserve sentences
    3. Fall back to word-boundary splitting for oversized sentences
    4. Add sentence-level overlap, not character-level overlap

    This prevents chunks from starting in the middle of words or sentences.
    """

    paragraphs = split_into_paragraphs(text)
    raw_chunks: List[str] = []
    current_sentences: List[str] = []

    def current_text() -> str:
        return " ".join(current_sentences).strip()

    def flush_current() -> None:
        nonlocal current_sentences
        text_to_add = current_text()
        if text_to_add:
            raw_chunks.append(text_to_add)
        current_sentences = []

    for paragraph in paragraphs:
        sentences = split_into_sentences(paragraph)

        for sentence in sentences:
            if len(sentence) > target_size:
                flush_current()
                raw_chunks.extend(split_oversized_sentence(sentence, target_size))
                continue

            candidate = " ".join(current_sentences + [sentence]).strip()

            if len(candidate) <= target_size:
                current_sentences.append(sentence)
            else:
                flush_current()
                current_sentences.append(sentence)

    flush_current()

    if not raw_chunks:
        return []

    chunks_with_overlap: List[str] = []

    for index, chunk in enumerate(raw_chunks):
        if index == 0:
            chunks_with_overlap.append(chunk)
            continue

        previous_sentences = split_into_sentences(raw_chunks[index - 1])
        overlap_sentences = previous_sentences[-CHUNK_OVERLAP_SENTENCES:]
        overlap_text = " ".join(overlap_sentences).strip()

        if overlap_text:
            chunks_with_overlap.append(f"{overlap_text} {chunk}".strip())
        else:
            chunks_with_overlap.append(chunk)

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