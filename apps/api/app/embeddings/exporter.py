import json
from pathlib import Path
from typing import List

from app.chunking.schemas import TextChunk
from app.embeddings.provider import EmbeddingProvider
from app.embeddings.schemas import ChunkEmbedding


def create_chunk_embeddings(
    chunks: List[TextChunk],
    provider: EmbeddingProvider,
) -> List[ChunkEmbedding]:
    texts = [chunk.text for chunk in chunks]
    vectors = provider.embed_texts(texts)

    embedded_chunks = []

    for chunk, vector in zip(chunks, vectors):
        embedded_chunks.append(
            ChunkEmbedding(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                source_type=chunk.source_type,
                trust_level=chunk.trust_level,
                section=chunk.section,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                text=chunk.text,
                embedding_model=provider.model_name(),
                embedding=vector,
            )
        )

    return embedded_chunks


def export_chunk_embeddings(
    document_id: str,
    embeddings: List[ChunkEmbedding],
    output_dir: str = "outputs/embeddings",
) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / f"{document_id}_embeddings.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            [embedding.model_dump() for embedding in embeddings],
            file,
            indent=2,
            ensure_ascii=False,
        )

    return str(output_path)
