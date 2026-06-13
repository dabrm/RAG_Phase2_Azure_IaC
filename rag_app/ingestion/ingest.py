from pathlib import Path
from loaders.wiki_loader import load_wikipedia_html
from rag_app.ingestion.chunking import chunk_text,DEFAULT_STRATEGY
from rag_app.ingestion.indexing import chunks_to_search_documents,upload_documents


DATA_DIR = Path("data")


def ingest_html_file(html_file: Path):

    print(f"Loading: {html_file.name}")

    text = load_wikipedia_html(str(html_file))

    chunks = chunk_text(
        text=text,
        source=html_file.name,
        title=html_file.stem,
        strategy=DEFAULT_STRATEGY
    )

    print(f"Created {len(chunks)} chunks")

    documents = chunks_to_search_documents(chunks)
    upload_documents(documents)

    print(f"Uploaded {len(documents)} documents")


def run_ingestion():

    html_files = list(DATA_DIR.glob("*.html"))

    if not html_files:
        raise ValueError(f"No html files found in {DATA_DIR}")

    for html_file in html_files:
        ingest_html_file(html_file)

    print(f"Finished ingestion of {len(html_files)} files")


if __name__ == "__main__":
    run_ingestion()