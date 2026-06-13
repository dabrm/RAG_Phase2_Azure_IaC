from typing import List

from rag_app.core.clients import get_search_client
from rag_app.ingestion.chunking import Chunk
from rag_app.ingestion.embeddings import generate_embeddings


def chunks_to_search_documents(chunks: List[Chunk]) -> List[dict]:

    chunk_texts = [chunk.content for chunk in chunks ]

    embeddings = generate_embeddings(chunk_texts)

    documents = []

    for chunk, embedding in zip(chunks, embeddings):

        documents.append(
            {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "contentVector": embedding,
                "source": chunk.source,
                "title": chunk.title,
                "chunk_index": chunk.chunk_index,
                "strategy_name": chunk.strategy_name
            }
        )

    return documents


def upload_documents(documents: List[dict]):

    search_client = get_search_client()

    return search_client.upload_documents(documents=documents)