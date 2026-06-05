import re
from typing import Optional


SECTION_PATTERNS = {
    "abstract": r"^\s*(abstract)\s*$",
    "introduction": r"^\s*(introduction|background)\s*$",
    "methods": r"^\s*(methods|materials and methods|methodology)\s*$",
    "results": r"^\s*(results|findings)\s*$",
    "discussion": r"^\s*(discussion)\s*$",
    "conclusion": r"^\s*(conclusion|conclusions)\s*$",
    "references": r"^\s*(references|bibliography)\s*$",
}


def detect_section_from_text(text: str) -> Optional[str]:
    """
    Detects the first recognizable scientific section heading in page text.

    This is a simple baseline detector.
    Later, we will improve this using layout-aware parsing.
    """

    lines = text.splitlines()

    for line in lines[:40]:
        stripped = line.strip().lower()

        if not stripped:
            continue

        for section_name, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, stripped, flags=re.IGNORECASE):
                return section_name

    return None
