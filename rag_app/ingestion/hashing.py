from datetime import datetime, timezone
from pathlib import Path
import hashlib
import uuid

from rag_app.core.clients import get_search_client
from rag_app.core.config import settings

def compute_content_hash(content: str) -> str:
    """
    SHA256 hash of chunk contents.
    Used for chunk-level deduplication.
    """

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

def compute_file_hash(path: Path) -> str:
    """
    SHA256 hash of file contents.
    """

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def is_already_ingested(
    file_hash: str,
    strategy_name: str,
    embedding_model: str
) -> bool:

    ingestion_client = get_search_client(
        settings.azure_search_ingestion_index_name
    )

    filter_expression = (
        f"file_hash eq '{file_hash}' "
        f"and strategy_name eq '{strategy_name}' "
        f"and embedding_model eq '{embedding_model}'"
    )

    results = ingestion_client.search(
        search_text="*",
        filter=filter_expression,
        top=1
    )

    return any(results)


def mark_as_ingested(
    file_hash: str,
    source: str,
    strategy_name: str,
    embedding_model: str
):

    ingestion_client = get_search_client(
        settings.azure_search_ingestion_index_name
    )

    document = {
        "hash_id": str(uuid.uuid4()),
        "file_hash": file_hash,
        "source": source,
        "strategy_name": strategy_name,
        "embedding_model": embedding_model,
        "ingested_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    ingestion_client.upload_documents(
        documents=[document]
    )