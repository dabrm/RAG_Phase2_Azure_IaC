from fastapi import FastAPI
from pydantic import BaseModel

from rag_app.generation.generate import generate_answer


app = FastAPI(title=" 'The Hobbit' RAG Platform")


class QueryRequest(BaseModel):
    question: str


@app.post("/chat")
async def chat(request: QueryRequest):

    answer = generate_answer(request.question)

    return {
        "question": request.question,
        "answer": answer
    }