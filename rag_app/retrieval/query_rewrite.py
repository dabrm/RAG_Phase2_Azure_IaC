from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings


SYSTEM_PROMPT = """
You are a query rewriting engine for a Retrieval-Augmented Generation (RAG) system.

Your job is to rewrite user questions into optimized search queries for a vector database containing Wikipedia articles about The Hobbit and Middle-earth.

Rules:
- Expand entity names (characters, places, objects)
- Add relevant synonyms and canonical names
- Remove conversational wording
- Preserve meaning
- Output ONLY the rewritten query
- No explanations
"""


def rewrite_query(query: str) -> str:
    query = query.strip()

    if not query:
        return query

    client = get_openai_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Rewrite this query:\n\n{query}"
        }
    ]

    response = client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=messages,
        temperature=0.0
    )

    rewritten = response.choices[0].message.content.strip()

    # safety fallback
    return rewritten if rewritten else query