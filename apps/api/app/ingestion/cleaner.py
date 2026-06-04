import re


def clean_text(text: str) -> str:
    """
    Basic text cleaner for extracted PDF text.

    Current scope:
    - normalize whitespace
    - remove excessive newlines
    - remove leading/trailing spaces

    We will improve this later for:
    - headers/footers
    - broken scientific text
    - references
    - table noise
    """

    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
