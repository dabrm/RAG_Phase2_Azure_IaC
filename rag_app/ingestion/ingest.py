from pathlib import Path
from loaders.wiki_loader import load_wikipedia_html
from rag_app.ingestion.chunking import chunk_text,DEFAULT_STRATEGY
from rag_app.ingestion.indexing import chunks_to_search_documents,upload_documents
from rag_app.core.config import settings
from rag_app.ingestion.hashing import compute_file_hash,is_already_ingested,mark_as_ingested


DATA_DIR = Path(settings.data_directory)


def ingest_html_file(html_file: Path):

    file_hash = compute_file_hash(html_file)

    embedding_model = (
        settings.azure_openai_embedding_deployment
    )

    if is_already_ingested(
        file_hash=file_hash,
        strategy_name=DEFAULT_STRATEGY.strategy_name,
        embedding_model=embedding_model
    ):
        print(
            f"Skipping already-ingested file: "
            f"{html_file.name}"
        )
        return

    print(f"Loading: {html_file.name}")

    text = load_wikipedia_html(
        str(html_file)
    )

    chunks = chunk_text(
        text=text,
        source=html_file.name,
        title=html_file.stem,
        strategy=DEFAULT_STRATEGY
    )

    print(
        f"Created {len(chunks)} chunks"
    )

    documents = chunks_to_search_documents(
        chunks
    )

    upload_documents(documents)

    mark_as_ingested(
        file_hash=file_hash,
        source=html_file.name,
        strategy_name=DEFAULT_STRATEGY.strategy_name,
        embedding_model=embedding_model
    )

    print(
        f"Uploaded {len(documents)} documents"
    )


def run_ingestion():

    html_files = list(
        DATA_DIR.glob("*.html")
    )

    if not html_files:
        raise ValueError(
            f"No html files found in {DATA_DIR}"
        )

    for html_file in html_files:
        ingest_html_file(html_file)

    print(
        f"Finished ingestion of "
        f"{len(html_files)} files"
    )


if __name__ == "__main__":
    run_ingestion()