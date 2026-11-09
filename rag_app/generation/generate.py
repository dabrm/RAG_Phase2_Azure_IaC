import time
from dataclasses import dataclass

from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings

from rag_app.retrieval.retrieve import (
    retrieve,
    RetrievedChunk
)

from rag_app.generation.prompts import SYSTEM_PROMPT
from rag_app.core.logging import logger


@dataclass
class GenerationResult:
    """
    Output of the generation pipeline.

    answer:
        Final LLM response.

    sources:
        Retrieved chunks used to construct
        the prompt context.
    """

    answer: str
    sources: list[RetrievedChunk]

def generate_answer(question: str):

    total_start = time.perf_counter()

    # Retrieval
    start = time.perf_counter()

    retrieval = retrieve(question)

    print(
        f"[TIMING] retrieval: "
        f"{time.perf_counter() - start:.3f}s"
    )

    context = retrieval.context

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""Context:
--- BEGIN CONTEXT ---
{context}
--- END CONTEXT ---

Question:
{question}
"""
        }
    ]

    # Generation
    start = time.perf_counter()

    openai_client = get_openai_client()

    print(f"[TIMING] context length: {len(context)} chars")

    generation_start = time.perf_counter()

    response = openai_client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=messages,
        # gpt-5-mini accepts  minimal/low/medium (the default) and high. 
        # # For RAG, where the answer is already in the context, minimal or low is usually enough and much faster.
        reasoning_effort="minimal", 
    )

    generation_end = time.perf_counter()

    print(f"[TIMING] Azure OpenAI generation API call: "
    f"{generation_end - generation_start:.3f}s")

    print(
        f"[TIMING] generation: "
        f"{time.perf_counter() - start:.3f}s"
    )

    print(
        f"[TIMING] generate_answer total: "
        f"{time.perf_counter() - total_start:.3f}s"
    )

    # guardrail for None in response (rare, but could happen if you're out of tokens etc)
    # without it, Streamlit would crash, as it does not accept None values
    choice = response.choices[0]
    answer = choice.message.content
    
    if not answer or not answer.strip():
        logger.warning("Empty answer from model. finish_reason=%s", choice.finish_reason)
        answer = "I couldn't generate an answer for that question. Please try rephrasing it."

    # proceed with normal  return of results
    return GenerationResult(
        answer=answer
        ,sources=retrieval.chunks
        )
