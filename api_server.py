from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
from main import get_question, get_ans, get_top_chunks, recipient_context, question_stack, go_back, reset_all

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Allow all origins by default
    # You can specify specific origins if needed
    allow_origins=[
        "http://localhost:8080",  # local development
        "https://slash-rag-agent.onrender.com",  # deployed backend
        "https://slash-experiences.netlify.app",  # deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    try:
        question = get_question()
        return {"question": question}
    except Exception as e:
        return {"error": str(e)}


@app.post("/submit")
async def submit(req: SubmitRequest):
    try:
        key = get_ans(req.ans)
        return {"status": "ok", "key": key}
    except Exception as e:
        print("❌ Error in /submit:", str(e))  # <--- add this line
        return {"status": "error", "message": str(e)}


@app.get("/next")
async def next_question():
    """
    Return the next question.
    """
    try:
        question = get_question()
        return {"question": question}
    except Exception as e:
        return {"error": str(e)}


@app.get("/suggestion")
async def suggestion(query: str = "", k: int = 5):
    """
    Return suggestions using get_top_chunks().
    """
    try:
        if query:
            chunks = get_top_chunks(query, k=k)
        else:
            # Try to use the current context as a query if query is not provided
            from main import format_final_prompt
            prompt = format_final_prompt()
            chunks = get_top_chunks(prompt, k=k)
        return {"suggestions": chunks}
    except Exception as e:
        return {"error": str(e)}


@app.get("/context")
async def context():
    """
    Return recipient_context and question_stack.
    """
    try:
        # Convert question_stack (list of tuples) to a serializable form
        stack_serializable = [
            {"key": key, "question": question, "answer": answer}
            for (key, question, answer) in question_stack
        ]
        return {
            "recipient_context": recipient_context,
            "question_stack": stack_serializable
        }
    except Exception as e:
        return {"error": str(e)}


# Add endpoint for going back to previous question
@app.get("/back")
async def back():
    """
    Go back to the previous question.
    """
    try:
        result = go_back()
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"error": str(e)}


@app.get("/reset")
async def reset():
    """
    Reset all stored context and start fresh.
    """
    try:
        reset_all()
        return {"status": "ok", "message": "Session reset successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# FastAPI startup event logger
@app.on_event("startup")
async def startup_event():
    print("✅ FastAPI app is live and running!")