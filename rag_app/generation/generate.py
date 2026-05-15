from core.clients import openai_client
from core.config import settings

from retrieval.retrieve import retrieve_context
from generation.prompts import SYSTEM_PROMPT


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

    response = openai_client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content