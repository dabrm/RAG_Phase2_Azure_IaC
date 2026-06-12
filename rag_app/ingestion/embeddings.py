from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings


def generate_embedding(text: str):
    openai_client = get_openai_client()
    response = openai_client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=text
    )

    return response.data[0].embedding