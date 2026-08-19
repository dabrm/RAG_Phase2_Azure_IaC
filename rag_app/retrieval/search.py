from dataclasses import dataclass
from typing import List, Optional
import time

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
    score: Optional[dict] = None


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
    total_start = time.perf_counter() # simple time-logging - overal start

    start = time.perf_counter() # query rewrite start 

    # query = rewrite_query(query) # skipping query rewrite for performance reasons (one LLM call less)

    print(
    f"[TIMING] query rewrite: "
    f"{time.perf_counter() - start:.3f}s"
    )

    if not query:
        raise ValueError("Query cannot be empty.")

    # 1. Create embedding for semantic search
    start = time.perf_counter()

    embedding = generate_embeddings([query])[0]

    print(
    f"[TIMING] query embedding: "
    f"{time.perf_counter() - start:.3f}s"
    )

    vector_query = _build_vector_query(embedding)

    search_client = get_search_client(settings.azure_search_index_name)

    # 2. Hybrid search (vector + keyword)
    start = time.perf_counter()

    results = search_client.search(
        search_text=query,  # keyword boost for entity matching (Smaug, Bilbo, etc.)
        vector_queries=[vector_query],
        select=["content", "source", "title", "chunk_index"]
    )

    # 3. Normalize results
    output: List[SearchResultChunk] = []

    for r in results:

        score = r.get("@search.score")

        if isinstance(score, dict):
            score = None

        output.append(
            SearchResultChunk(
                content=r.get("content", ""),
                source=r.get("source", ""),
                title=r.get("title", ""),
                chunk_index=r.get("chunk_index", 0),
                score=float(score) if score is not None else None
                )
                )
    print(
    f"[TIMING] Azure AI Search: "
    f"{time.perf_counter() - start:.3f}s"
    )

    print(
    f"[TIMING] vector_search total: "
    f"{time.perf_counter() - total_start:.3f}s")

    # 4. Guard: no results
    if not output:
        return []

    return output