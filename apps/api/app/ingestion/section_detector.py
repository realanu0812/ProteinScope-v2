import re
from typing import List, Optional

from app.ingestion.schemas import PageText, SectionBlock


COMMON_SECTION_ALIASES = {
    "abstract": ["abstract"],
    "introduction": ["introduction", "background"],
    "methods": ["methods", "methodology", "materials and methods", "experimental methods"],
    "results": ["results", "findings"],
    "discussion": ["discussion"],
    "results_discussion": ["results and discussion", "results & discussion"],
    "conclusion": ["conclusion", "conclusions", "summary"],
    "references": ["references", "bibliography"],
}


IGNORE_PREFIXES = (
    "figure",
    "fig.",
    "table",
    "journal",
    "received",
    "accepted",
    "copyright",
)


def slugify_heading(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9α-ωΑ-Ω]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def normalize_heading(line: str) -> str:
    line = line.strip()

    line = line.replace("ˆ", "")
    line = line.replace("β", "beta")
    line = line.replace("α", "alpha")
    line = line.replace("￾", "")

    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"^\d+(\.\d+)*\.?\s+", "", line)
    line = re.sub(r"[:.\-–—]+$", "", line)

    return line.strip()


def is_likely_heading(line: str) -> bool:
    raw = line.strip()
    normalized = normalize_heading(raw)

    if not normalized:
        return False

    lowered = normalized.lower()

    if lowered.startswith(IGNORE_PREFIXES):
        return False

    word_count = len(normalized.split())

    if word_count < 1 or word_count > 14:
        return False

    if len(normalized) > 110:
        return False

    if normalized.endswith((".", ",", ";")):
        return False

    alpha_chars = sum(char.isalpha() for char in normalized)

    if alpha_chars < 4:
        return False

    uppercase_letters = sum(char.isupper() for char in raw if char.isalpha())
    total_letters = sum(char.isalpha() for char in raw)

    uppercase_ratio = uppercase_letters / total_letters if total_letters else 0

    is_mostly_uppercase = uppercase_ratio >= 0.75 and word_count >= 2

    words = normalized.split()
    title_case_words = sum(
        1 for word in words
        if word[:1].isupper() and len(word) > 2
    )
    is_title_case = word_count >= 2 and title_case_words >= max(1, word_count * 0.6)

    return is_mostly_uppercase or is_title_case


def detect_common_section(line: str) -> Optional[str]:
    normalized = normalize_heading(line).lower()

    for section_name, aliases in COMMON_SECTION_ALIASES.items():
        if normalized in aliases:
            return section_name

    return None


def detect_section_from_line(line: str) -> Optional[str]:
    common_section = detect_common_section(line)

    if common_section:
        return common_section

    if is_likely_heading(line):
        return slugify_heading(normalize_heading(line))

    return None


def build_section_blocks(pages: List[PageText]) -> List[SectionBlock]:
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
                current_lines = [line]
            else:
                if current_start_page is None:
                    current_start_page = page.page_number

                current_end_page = page.page_number
                current_lines.append(line)

    flush_current_block()

    return blocks