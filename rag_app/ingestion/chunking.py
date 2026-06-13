from dataclasses import dataclass
from typing import List
import uuid

@dataclass
class Chunk:
    chunk_id: str
    content: str
    chunk_index: int
    source: str
    title: str
    strategy_name: str

@dataclass
class ChunkingStrategy:

    # Core chunking parameters
    chunk_size: int = 500 # measured in characters
    chunk_overlap: int = 50

    # Splitting behavior
    split_on_paragraphs: bool = True
    preserve_sentence_boundaries: bool = True # placeholder, no logic yet

    # Metadata
    strategy_name: str = "default"


DEFAULT_STRATEGY = ChunkingStrategy()


SMALL_CHUNKS_STRATEGY = ChunkingStrategy(
    chunk_size=300,
    chunk_overlap=30,
    strategy_name="small_chunks"
)


LARGE_CHUNKS_STRATEGY = ChunkingStrategy(
    chunk_size=1000,
    chunk_overlap=100,
    strategy_name="large_chunks"
)


# orchestration separated from policy
# clean ingestion pipeline,  easy experimentation
def 
(
    text: str,
    source: str,
    title: str,
    strategy: ChunkingStrategy
) -> List[Chunk]:

    # Normalize whitespace
    text = text.strip()

    # Split into paragraphs
    if strategy.split_on_paragraphs:
        paragraphs = [
            p.strip()
            for p in text.split("\n\n") # double-newline -> usually new paragraph
            if p.strip()
        ]
    else:
        paragraphs = [text]


    # Build chunks
    chunks = []
    current_chunk = ""
    chunk_index = 0

    for paragraph in paragraphs:
        # If paragraph fits -> append
        if len(current_chunk) + len(paragraph) < strategy.chunk_size:
            current_chunk += "\n\n" + paragraph

        # Otherwise finalize chunk
        else:
            chunk = Chunk(
                chunk_id=str(uuid.uuid4()),
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                source=source,
                title=title,
                strategy_name=strategy.strategy_name
            )

            chunks.append(chunk)

            # Overlap handling
            overlap_text = current_chunk[ - strategy.chunk_overlap:]
            current_chunk = overlap_text + "\n\n" + paragraph
            chunk_index += 1

    # Final chunk
    if current_chunk.strip(): # is cleaned chunk non-empty ("" == False in Python)
        chunk = Chunk(
            chunk_id=str(uuid.uuid4()),
            content=current_chunk.strip(),
            chunk_index=chunk_index,
            source=source,
            title=title,
            strategy_name=strategy.strategy_name
        )

        chunks.append(chunk)

    return chunks