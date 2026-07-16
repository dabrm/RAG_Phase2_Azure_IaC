from dataclasses import dataclass
from typing import List, Optional

from rag_app.retrieval.search import vector_search



@dataclass
class RetrievedChunk:
    content: str
    source: str
    title: str
    chunk_index: int
    score: Optional[dict] = None

# ----------------------------
# Structured retrieval object (dataclass instead of dictionary)
# ----------------------------
@dataclass
class RetrievalResult:
    """
    Structured output of the retrieval pipeline.

    context:
        Formatted string injected into the LLM prompt.

    chunks:
        Original retrieved chunks with metadata.
    """

    context: str
    chunks: List[RetrievedChunk]

# ----------------------------
# Deduplication (smarter)
# ----------------------------
def _deduplicate(docs: List[RetrievedChunk]) -> List[RetrievedChunk]:
    """
    Deduplicates using a stronger key:
    (source + chunk_index + first 200 chars)
    """

    seen = set()
    unique = []

    for d in docs:
        key = (
            d.source,
            d.chunk_index,
            d.content[:200]
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(d)

    return unique


# ----------------------------
# Context formatting
# ----------------------------
def _format_chunk(doc: RetrievedChunk) -> str:
    return (
        f"[Source: {doc.source} | Title: {doc.title} | Chunk: {doc.chunk_index} | Score: {doc.score}]\n"
        f"{doc.content.strip()}"
    )


# ----------------------------
# Context builder (core logic)
# ----------------------------
def retrieve(query: str, top_k: int = 5, max_chars: int = 12000) -> RetrievalResult:
    """
    End-to-end retrieval pipeline:
    search → normalize → dedup → rank → budget → format
    """

    raw_results = vector_search(query)

    if not raw_results:
        return RetrievalResult(
            context=""
            ,chunks=[]
            )

    # 1. normalize results
    results: List[RetrievedChunk] = []
    for r in raw_results:
        results.append(
            RetrievedChunk(
            content=r.content,
            source=r.source,
            title=r.title,
            chunk_index=r.chunk_index,
            score=r.score
        )
    )

    # 2. deduplicate
    results = _deduplicate(results)

    # 3. score-aware sorting (critical upgrade)
    results.sort(
    key=lambda x: float(x.score) if x.score is not None else 0.0,
    reverse=True
)

    # 4. top_k cutoff
    results = results[:top_k]

    # 5. context budgeting (simple but effective)
    selected = []
    total_chars = 0

    for r in results:
        chunk_len = len(r.content)

        if total_chars + chunk_len > max_chars:
            break

        selected.append(r)
        total_chars += chunk_len

    # 6. format final context
    formatted = [ _format_chunk(doc) for doc in selected ]

    context = "\n\n---\n\n".join(formatted)

    return RetrievalResult(
        context=context
        ,chunks=selected
        )
