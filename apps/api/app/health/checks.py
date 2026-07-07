import os

from app.ingestion.grobid_client import GrobidClient
from app.vector_store.qdrant_store import QdrantVectorStore


def check_qdrant() -> dict:
    try:
        vector_store = QdrantVectorStore()
        vector_store.client.get_collections()

        return {
            "status": "ok",
            "message": "Qdrant is reachable",
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }


def check_grobid() -> dict:
    client = GrobidClient()

    if client.is_alive():
        return {
            "status": "ok",
            "message": "GROBID is reachable",
        }

    return {
        "status": "error",
        "message": "GROBID is not reachable",
    }


def check_llm_config() -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if api_key and model:
        return {
            "status": "ok",
            "message": f"Groq configured with model: {model}",
        }

    return {
        "status": "warning",
        "message": "GROQ_API_KEY or GROQ_MODEL is missing",
    }


def run_health_checks() -> dict:
    checks = {
        "qdrant": check_qdrant(),
        "grobid": check_grobid(),
        "llm": check_llm_config(),
    }

    overall_status = "ok"

    if any(check["status"] == "error" for check in checks.values()):
        overall_status = "error"
    elif any(check["status"] == "warning" for check in checks.values()):
        overall_status = "warning"

    return {
        "status": overall_status,
        "checks": checks,
    }
