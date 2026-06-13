from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings


def generate_embeddings(texts: list[str]):

    openai_client = get_openai_client()

    response = openai_client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=texts
    )

    return [item.embedding for item in response.data ] # allowing batch-embeddings for multiple cunks