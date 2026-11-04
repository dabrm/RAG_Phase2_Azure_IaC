import random
import time
from typing import List
from openai import APIConnectionError, RateLimitError


from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings
from rag_app.core.logging import logger

MAX_ATTEMPTS = 6

def _embed_with_retry(texts: List[str]):
    client = get_openai_client()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return client.embeddings.create(
                model=settings.azure_openai_embedding_deployment,
                input=texts,
            )
        # APITimeoutError is a subclass of APIConnectionError
        except (APIConnectionError, RateLimitError) as exc:
            if attempt == MAX_ATTEMPTS:
                raise
            delay = min(60, 2 ** attempt) + random.random()
            logger.warning(
                "Embedding call failed (%s), attempt %d/%d, retrying in %.1fs",
                type(exc).__name__, attempt, MAX_ATTEMPTS, delay,
            )
            time.sleep(delay)

def generate_embeddings(texts: str | List[str]) -> List[List[float]]:

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        raise ValueError("No texts provided for embedding generation.")

    openai_client = get_openai_client()

    response = _embed_with_retry(texts)

    embeddings = [ item.embedding for item in response.data ]

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