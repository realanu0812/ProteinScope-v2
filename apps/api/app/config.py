import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    qdrant_url: str
    grobid_url: str
    groq_api_key: str | None
    groq_model: str


def get_config() -> AppConfig:
    return AppConfig(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        grobid_url=os.getenv("GROBID_URL", "http://localhost:8070"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    )


def validate_generation_config() -> None:
    config = get_config()

    if not config.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to apps/api/.env before using answer generation."
        )
