from dataclasses import dataclass
from typing import List, Optional

from azure.search.documents.models import VectorizedQuery

from rag_app.core.clients import get_search_client
from rag_app.ingestion.embeddings import generate_embeddings
from rag_app.core.config import settings
from rag_app.retrieval.query_rewrite import rewrite_query


@dataclass
class SearchResultChunk:
    content: str
    source: str
    title: str
    chunk_index: int
    score: Optional[float] = None


def _build_vector_query(embedding: List[float]) -> VectorizedQuery:
    return VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=settings.top_k_retrieval,
        fields="contentVector"
    )


def vector_search(query: str) -> List[SearchResultChunk]:
    """
    Hybrid vector search over Azure AI Search index.
    """

    query = query = rewrite_query(query)

    if not query:
        raise ValueError("Query cannot be empty.")

    # 1. Create embedding for semantic search
    embedding = generate_embeddings([query])[0]

    vector_query = _build_vector_query(embedding)

    search_client = get_search_client()

    # 2. Hybrid search (vector + keyword)
    results = search_client.search(
        search_text=query,  # keyword boost for entity matching (Smaug, Bilbo, etc.)
        vector_queries=[vector_query],
        select=["content", "source", "title", "chunk_index"]
    )

    # 3. Normalize results
    output: List[SearchResultChunk] = []

    for r in results:
        output.append(
            SearchResultChunk(
                content=r.get("content", ""),
                source=r.get("source", ""),
                title=r.get("title", ""),
                chunk_index=r.get("chunk_index", 0),
                score=getattr(r, "@search.score", None)
            )
        )

    # 4. Guard: no results
    if not output:
        return []

    return output