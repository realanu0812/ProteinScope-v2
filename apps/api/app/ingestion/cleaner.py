import re


def normalize_whitespace(text: str) -> str:
    """
    Normalizes common whitespace issues from PDF extraction.
    """

    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")

    # Replace tabs and repeated spaces with single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    # Collapse too many blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_standalone_page_numbers(text: str) -> str:
    """
    Removes lines that are only page numbers.

    Example removed:
    1
    23
    Page 4
    """

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        if re.fullmatch(r"\d{1,4}", stripped):
            continue

        if re.fullmatch(r"page\s+\d{1,4}", stripped, flags=re.IGNORECASE):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def is_useful_text(text: str, min_chars: int = 50) -> bool:
    """
    Checks whether extracted page text is useful enough to keep.

    This helps detect:
    - blank pages
    - scanned pages with no OCR
    - pages with only headers/footers
    """

    if not text:
        return False

    alpha_chars = sum(char.isalpha() for char in text)

    return len(text.strip()) >= min_chars and alpha_chars >= min_chars * 0.4


def clean_text(text: str) -> str:
    """
    Main text cleaning pipeline.

    Important:
    This is intentionally conservative.
    We do not aggressively delete text yet because scientific PDFs may contain:
    - gene names
    - protein IDs
    - abbreviations
    - equations
    - table fragments
    """

    text = normalize_whitespace(text)
    text = remove_standalone_page_numbers(text)
    text = normalize_whitespace(text)

    return text
