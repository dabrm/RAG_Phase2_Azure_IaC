from rag_app.core.clients import get_search_client
from rag_app.ingestion.embeddings import generate_embedding
from rag_app.core.config import settings


def vector_search(query: str):

    embedding = generate_embedding(query)

    results = get_search_client.search(
        search_text=None,
        vector_queries=[
            {
                "kind": "vector",
                "vector": embedding,
                "fields": "contentVector",
                "k": settings.top_k_retrieval
            }
        ],
        select=["content", "source"]
    )

    return list(results)