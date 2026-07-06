import os
from pathlib import Path

import requests


class GrobidClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (
            base_url
            or os.getenv("GROBID_URL", "http://localhost:8070")
        ).rstrip("/")

    def is_alive(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/isalive", timeout=5)
            return response.text.strip().lower() == "true"
        except requests.RequestException:
            return False

    def process_fulltext_document(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        with path.open("rb") as file:
            response = requests.post(
                f"{self.base_url}/api/processFulltextDocument",
                files={"input": file},
                data={"consolidateHeader": "1", "consolidateCitations": "0"},
                timeout=120,
            )

        response.raise_for_status()
        return response.text
