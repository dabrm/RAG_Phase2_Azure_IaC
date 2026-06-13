from azure.search.documents.models import VectorizedQuery

from rag_app.core.clients import get_search_client
from rag_app.ingestion.embeddings import generate_embeddings
from rag_app.core.config import settings


def vector_search(query: str):
    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    embedding = generate_embeddings([query])[0]

    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=settings.top_k_retrieval,
        fields="contentVector"
    )

    search_client = get_search_client()

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["content","source","title","chunk_index"]
    )

    return list(results)