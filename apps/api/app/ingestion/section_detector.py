import re
from typing import List, Optional, Tuple

from .schemas import PageText, SectionBlock


SECTION_ALIASES = {
    "abstract": [
        "abstract",
    ],
    "introduction": [
        "introduction",
        "background",
    ],
    "methods": [
        "methods",
        "methodology",
        "materials and methods",
        "experimental procedures",
        "experimental methods",
    ],
    "results": [
        "results",
        "findings",
    ],
    "discussion": [
        "discussion",
    ],
    "results_discussion": [
        "results and discussion",
        "results & discussion",
    ],
    "conclusion": [
        "conclusion",
        "conclusions",
        "summary",
    ],
    "references": [
        "references",
        "bibliography",
    ],
}


def normalize_heading(line: str) -> str:
    line = line.strip().lower()

    # Handles:
    # 1 Introduction
    # 1. Introduction
    # 2.1 Materials and Methods
    line = re.sub(r"^\d+(\.\d+)*\.?\s+", "", line)

    # Remove trailing punctuation
    line = re.sub(r"[:.\-–—]+$", "", line)

    # Normalize internal spaces
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def detect_section_from_line(line: str) -> Optional[str]:
    normalized = normalize_heading(line)

    if not normalized:
        return None

    # Avoid false positives from full sentences
    if len(normalized.split()) > 6:
        return None

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section_name

    return None


def find_section_headings(text: str) -> List[Tuple[int, str, str]]:
    """
    Finds all section headings in a page.

    Returns:
    (line_index, section_name, original_line)
    """

    headings = []
    lines = text.splitlines()

    for index, line in enumerate(lines):
        section = detect_section_from_line(line)

        if section:
            headings.append((index, section, line))

    return headings


def build_section_blocks(pages: List[PageText]) -> List[SectionBlock]:
    """
    Converts page-wise text into section-aware blocks.

    Why this exists:
    A single page may contain Abstract + Introduction.
    Page-level section labels are too coarse for scientific RAG.
    """

    blocks: List[SectionBlock] = []

    current_section: Optional[str] = None
    current_lines: List[str] = []
    current_start_page: Optional[int] = None
    current_end_page: Optional[int] = None

    def flush_current_block():
        nonlocal current_lines, current_section, current_start_page, current_end_page

        text = "\n".join(current_lines).strip()

        if text and current_start_page is not None and current_end_page is not None:
            blocks.append(
                SectionBlock(
                    section=current_section,
                    text=text,
                    start_page=current_start_page,
                    end_page=current_end_page,
                    char_count=len(text),
                )
            )

        current_lines = []

    for page in pages:
        lines = page.text.splitlines()

        for line in lines:
            detected_section = detect_section_from_line(line)

            if detected_section:
                flush_current_block()
                current_section = detected_section
                current_start_page = page.page_number
                current_end_page = page.page_number

                # Keep heading line inside block for context
                current_lines = [line]
            else:
                if current_start_page is None:
                    current_start_page = page.page_number

                current_end_page = page.page_number
                current_lines.append(line)

    flush_current_block()

    return blocks
