from core.clients import openai_client
from core.config import settings


def generate_embedding(text: str):

    response = openai_client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=text
    )

    return response.data[0].embedding