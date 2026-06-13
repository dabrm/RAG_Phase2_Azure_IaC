from typing import List

from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings


def generate_embeddings(texts: str | List[str]) -> List[List[float]]:

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        raise ValueError("No texts provided for embedding generation.")

    openai_client = get_openai_client()

    response = openai_client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=texts
    )

    embeddings = [
        item.embedding
        for item in response.data
    ]

    if len(embeddings) != len(texts):
        raise ValueError(
            f"Embedding count mismatch. "
            f"Inputs={len(texts)}, "
            f"Embeddings={len(embeddings)}"
        )

    for embedding in embeddings:
        if len(embedding) != settings.embedding_dimensions:
            raise ValueError(
                f"Unexpected embedding dimension. "
                f"Expected={settings.embedding_dimensions}, "
                f"Actual={len(embedding)}"
            )

    return embeddings