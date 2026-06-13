from dataclasses import dataclass
from typing import List
import uuid
import re


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
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Splitting behavior
    split_on_paragraphs: bool = True
    preserve_sentence_boundaries: bool = True

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

# avoid mid-word splitting of the overlap
def get_overlap(text: str, overlap: int) -> str:
    words = text.split()

    result = []
    size = 0

    for word in reversed(words):
        size += len(word) + 1

        if size > overlap:
            break

        result.insert(0, word)

    return " ".join(result)

def split_long_text(text: str, max_size: int) -> List[str]:
    """
    Recursive splitter:
    paragraph -> sentence -> character fallback
    """

    text = text.strip()

    if len(text) <= max_size:
        return [text]

    # sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)

    if len(sentences) > 1:
        pieces = []

        current = ""

        for sentence in sentences:

            if len(sentence) > max_size:
                # recurse again (eventually hits char fallback)
                pieces.extend(split_long_text(sentence, max_size))
                continue

            candidate = (
                sentence
                if not current
                else current + " " + sentence
            )

            if len(candidate) <= max_size:
                current = candidate
            else:
                pieces.append(current)
                current = sentence

        if current:
            pieces.append(current)

        return pieces

    # character fallback
    return [
        text[i:i + max_size]
        for i in range(0, len(text), max_size)
    ]


def chunk_text(
    text: str,
    source: str,
    title: str,
    strategy: ChunkingStrategy
) -> List[Chunk]:

    text = text.strip()

    # Paragraph split
    if strategy.split_on_paragraphs:
        raw_paragraphs = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip()
        ]
    else:
        raw_paragraphs = [text]

    # Recursive expansion
    paragraphs = []

    for paragraph in raw_paragraphs:

        if len(paragraph) <= strategy.chunk_size:
            paragraphs.append(paragraph)
        else:
            paragraphs.extend(
                split_long_text(
                    paragraph,
                    strategy.chunk_size
                )
            )

    chunks = []
    current_chunk = ""
    chunk_index = 0

    for paragraph in paragraphs:

        if not current_chunk:
            current_chunk = paragraph
            continue

        candidate = current_chunk + "\n\n" + paragraph

        if len(candidate) <= strategy.chunk_size:
            current_chunk = candidate

        else:

            chunks.append(
                Chunk(
                    chunk_id=str(uuid.uuid4()),
                    content=current_chunk.strip(),
                    chunk_index=chunk_index,
                    source=source,
                    title=title,
                    strategy_name=strategy.strategy_name
                )
            )

            overlap_text = get_overlap(
                current_chunk,
                strategy.chunk_overlap
                )

            current_chunk = (
                overlap_text
                + "\n\n"
                + paragraph
            )

            # Safety guard
            if len(current_chunk) > strategy.chunk_size:
                current_chunk = current_chunk[
                    -strategy.chunk_size:
                ]

            chunk_index += 1

    # Final chunk
    if current_chunk.strip():

        chunks.append(
            Chunk(
                chunk_id=str(uuid.uuid4()),
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                source=source,
                title=title,
                strategy_name=strategy.strategy_name
            )
        )

    return chunks