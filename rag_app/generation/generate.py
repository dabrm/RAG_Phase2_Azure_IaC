from rag_app.core.clients import get_openai_client
from rag_app.core.config import settings

from rag_app.retrieval.retrieve import retrieve_context
from rag_app.generation.prompts import SYSTEM_PROMPT


def generate_answer(question: str):

    context = retrieve_context(question)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f'''
Context:
{context}

Question:
{question}
'''
        }
    ]
    openai_client = get_openai_client()

    response = openai_client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content