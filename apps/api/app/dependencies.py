from functools import lru_cache

from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.generation.groq_provider import GroqGenerationProvider
from app.reranking.reranker import CrossEncoderReranker
from app.vector_store.qdrant_store import QdrantVectorStore


@lru_cache(maxsize=1)
def get_embedding_provider() -> SentenceTransformerEmbeddingProvider:
    return SentenceTransformerEmbeddingProvider()


@lru_cache(maxsize=1)
def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore()


@lru_cache(maxsize=1)
def get_generation_provider() -> GroqGenerationProvider:
    return GroqGenerationProvider()


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoderReranker:
    return CrossEncoderReranker()
