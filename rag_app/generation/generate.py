from dataclasses import dataclass

from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings

from rag_app.retrieval.retrieve import (
    retrieve,
    RetrievedChunk
)

from rag_app.generation.prompts import SYSTEM_PROMPT


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

    retrieval = retrieve(question)
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
    openai_client = get_openai_client()

    response = openai_client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=messages,
        temperature=settings.temperature
    )

    return GenerationResult(
        answer=response.choices[0].message.content
        ,sources=retrieval.chunks
        )
