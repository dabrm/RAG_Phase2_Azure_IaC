from typing import List
import time

from rag_app.core.clients import (
    get_search_client,
    get_search_index_name
)
from rag_app.ingestion.chunking import Chunk
from rag_app.ingestion.embeddings import generate_embeddings
from rag_app.core.config import settings
from rag_app.ingestion.hashing import compute_content_hash


def chunks_to_search_documents(chunks: List[Chunk]) -> List[dict]:

    chunk_texts = [chunk.content for chunk in chunks]

    embeddings = []

    for i in range(
        0,
        len(chunk_texts),
        settings.embedding_batch_size
    ):
        batch = chunk_texts[
            i:i + settings.embedding_batch_size
        ]

        embeddings.extend(
            generate_embeddings(batch)
        )

        print(f"Embedded batch {i // settings.embedding_batch_size + 1}")
        time.sleep(11)

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Embedding count mismatch. "
            f"Chunks={len(chunks)}, "
            f"Embeddings={len(embeddings)}"
        )

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
                "strategy_name": chunk.strategy_name,
                "content_hash": compute_content_hash(chunk.content)
            }
        )

    return documents


def upload_documents(documents: List[dict]):

    search_client = get_search_client(get_search_index_name())

    results = search_client.upload_documents(
        documents=documents
    )

    failed = [
        result
        for result in results
        if not result.succeeded
    ]

    if failed:
        failed_keys = [
            result.key
            for result in failed
        ]

        raise RuntimeError(
            f"{len(failed)} document uploads failed. "
            f"Failed keys: {failed_keys}"
        )

    return results

def embed_and_upload(chunks: List[Chunk]) -> int:
    uploaded = 0
    size = settings.embedding_batch_size

    for i in range(0, len(chunks), size):
        batch = chunks[i:i + size]
        embeddings = generate_embeddings([c.content for c in batch])

        documents = [
            {
                "chunk_id": c.chunk_id,
                "content": c.content,
                "contentVector": emb,
                "source": c.source,
                "title": c.title,
                "chunk_index": c.chunk_index,
                "strategy_name": c.strategy_name,
                "content_hash": compute_content_hash(c.content),
            }
            for c, emb in zip(batch, embeddings)
        ]

        upload_documents(documents)
        uploaded += len(documents)
        print(f"Embedded + uploaded {uploaded}/{len(chunks)}")
        time.sleep(11)  # keep only while you're on the 6 req/min tier

    return uploaded