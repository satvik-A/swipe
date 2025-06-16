

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
from main import get_question, get_ans, get_top_chunks, recipient_context, question_stack

app = FastAPI()

# Models for request bodies
class SubmitRequest(BaseModel):
    ans: str

class SuggestionRequest(BaseModel):
    query: str = ""
    k: int = 5


@app.get("/init")
async def init():
    """
    Return the first Groq-generated question.
    """
    question = get_question()
    return {"question": question}


@app.post("/submit")
async def submit(req: SubmitRequest):
    """
    Store an answer.
    """
    
    key = get_ans(req.ans)
    return {"status": "ok", "key": key}


@app.get("/next")
async def next_question():
    """
    Return the next question.
    """
    question = get_question()
    return {"question": question}


@app.get("/suggestion")
async def suggestion(query: str = "", k: int = 5):
    """
    Return suggestions using get_top_chunks().
    """
    if query:
        chunks = get_top_chunks(query, k=k)
    else:
        # Try to use the current context as a query if query is not provided
        from main import format_final_prompt
        prompt = format_final_prompt()
        chunks = get_top_chunks(prompt, k=k)
    return {"suggestions": chunks}


@app.get("/context")
async def context():
    """
    Return recipient_context and question_stack.
    """
    # Convert question_stack (list of tuples) to a serializable form
    stack_serializable = [
        {"key": key, "question": question, "answer": answer}
        for (key, question, answer) in question_stack
    ]
    return {
        "recipient_context": recipient_context,
        "question_stack": stack_serializable
    }