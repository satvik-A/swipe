


from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
from main import ask_and_respond, go_back, format_final_prompt, query_groq, recipient_context, question_stack

app = FastAPI()
session_store: Dict[str, Dict] = {}

class AnswerInput(BaseModel):
    session_id: str
    question: str
    answer: str

class FollowUpInput(BaseModel):
    session_id: str
    message: str


# Create a new session
@app.post("/start-session")
def start_session():
    session_id = str(uuid4())
    session_store[session_id] = {
        "context": {},
        "stack": []
    }
    return {"session_id": session_id}

# Submit an answer
@app.post("/submit-answer")
def submit_answer(data: AnswerInput):
    session_id = data.session_id
    question = data.question
    answer = data.answer
    safe_key = "_".join(question.lower().split())[:40]
    session_store[session_id]["context"][safe_key] = answer
    session_store[session_id]["stack"].append((safe_key, question, answer))
    return {"status": "stored", "question": question, "answer": answer}

# Go back to the previous question
@app.post("/go-back")
def go_back_api(data: FollowUpInput):
    session_id = data.session_id
    if not session_store[session_id]["stack"]:
        return {"error": "No previous question to go back to."}
    key, question, answer = session_store[session_id]["stack"].pop()
    del session_store[session_id]["context"][key]
    return {"question": question, "answer": answer}

# Get final suggestion
@app.get("/suggestion")
def get_suggestion(session_id: str):
    context = session_store[session_id]["context"]
    prompt = "You are a creative and thoughtful assistant helping someone choose a unique experience gift. Based on the following details, suggest one highly relevant experience with a short reason:\n\n"
    for key, value in context.items():
        prompt += f"{key.replace('_', ' ').capitalize()}: {value}\n"
    prompt += "\nKeep it concise but vivid."
    ai_suggestion = query_groq([{"role": "user", "content": prompt}])
    return {"suggestion": ai_suggestion}

# Follow-up chat
@app.post("/follow-up")
def follow_up(data: FollowUpInput):
    context = session_store[data.session_id]["context"]
    context_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in context.items()])
    messages = [{"role": "user", "content": f"Here is what we know about the recipient:\n{context_summary}\nUser question: {data.message}"}]
    answer = query_groq(messages)
    return {"answer": answer}