from typing import List

from qdrant_client import QdrantClient # type: ignore
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams # type: ignore

from ..embeddings.schemas import ChunkEmbedding
from ..retrieval.schemas import SearchResult, SearchRequest


COLLECTION_NAME = "proteinscope_chunks"
VECTOR_SIZE = 384


class QdrantVectorStore:
    def __init__(self, url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=url)

    def ensure_collection(self) -> None:
        existing_collections = [
            collection.name
            for collection in self.client.get_collections().collections
        ]

        if COLLECTION_NAME in existing_collections:
            return

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def upsert_embeddings(self, embeddings: List[ChunkEmbedding]) -> int:
        self.ensure_collection()

        points = []

        for index, item in enumerate(embeddings):
            points.append(
                PointStruct(
                    id=item.chunk_id,
                    vector=item.embedding,
                    payload={
                        "chunk_id": item.chunk_id,
                        "document_id": item.document_id,
                        "chunk_index": item.chunk_index,
                        "source_type": item.source_type,
                        "trust_level": item.trust_level,
                        "section": item.section,
                        "start_page": item.start_page,
                        "end_page": item.end_page,
                        "text": item.text,
                        "embedding_model": item.embedding_model,
                    },
                )
            )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        return len(points)

    def search(
      self,
      query_vector: List[float],
      request: SearchRequest,
  ) -> List[SearchResult]:
      self.ensure_collection()

      must_conditions = []
      must_not_conditions = []

      if request.document_id:
          must_conditions.append(
              FieldCondition(
                  key="document_id",
                  match=MatchValue(value=request.document_id),
              )
          )

      if request.source_type:
          must_conditions.append(
              FieldCondition(
                  key="source_type",
                  match=MatchValue(value=request.source_type),
              )
          )

      if request.trust_level:
          must_conditions.append(
              FieldCondition(
                  key="trust_level",
                  match=MatchValue(value=request.trust_level),
              )
          )

      if request.section:
          must_conditions.append(
              FieldCondition(
                  key="section",
                  match=MatchValue(value=request.section),
              )
          )

      if not request.include_references:
          must_not_conditions.append(
              FieldCondition(
                  key="section",
                  match=MatchValue(value="references"),
              )
          )

      query_filter = None

      if must_conditions or must_not_conditions:
          query_filter = Filter(
              must=must_conditions or None,
              must_not=must_not_conditions or None,
          )

      results = self.client.search(
          collection_name=COLLECTION_NAME,
          query_vector=query_vector,
          query_filter=query_filter,
          limit=request.top_k,
      )

      search_results = []

      for result in results:
          payload = result.payload or {}

          search_results.append(
              SearchResult(
                  score=result.score,
                  chunk_id=payload.get("chunk_id"),
                  document_id=payload.get("document_id"),
                  chunk_index=payload.get("chunk_index"),
                  source_type=payload.get("source_type"),
                  trust_level=payload.get("trust_level"),
                  section=payload.get("section"),
                  start_page=payload.get("start_page"),
                  end_page=payload.get("end_page"),
                  text=payload.get("text"),
              )
          )

      return search_results