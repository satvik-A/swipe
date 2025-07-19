
# `api_server.py`

This file contains the FastAPI application that exposes the Slash RAG Agent's functionality through a RESTful API.

## 1. Endpoints

### 1.1. `GET /init`

- **Description:** Initializes a new session and returns the first question.
- **Response:**
    - `question`: The first question to ask the user.
    - `session_id`: A unique identifier for the session.

### 1.2. `POST /submit`

- **Description:** Submits an answer to the current question.
- **Request Body:**
    - `session_id`: The session ID.
    - `ans`: The user's answer to the question.
- **Response:**
    - `status`: "ok" if the submission was successful.
    - `key`: The key under which the answer was stored.

### 1.3. `GET /next`

- **Description:** Retrieves the next question in the sequence.
- **Query Parameters:**
    - `session_id`: The session ID.
- **Response:**
    - `question`: The next question to ask the user.

### 1.4. `GET /suggestion`

- **Description:** Gets gift suggestions based on the current context.
- **Query Parameters:**
    - `session_id`: The session ID.
    - `query` (optional): A query to search for.
    - `k` (optional): The number of suggestions to return.
- **Response:**
    - `suggestions`: A list of gift suggestions.

### 1.5. `GET /context`

- **Description:** Returns the current session's context.
- **Query Parameters:**
    - `session_id`: The session ID.
- **Response:**
    - `recipient_context`: A dictionary containing the user's answers.
    - `question_stack`: A list of questions that have been asked.

### 1.6. `GET /back`

- **Description:** Goes back to the previous question.
- **Query Parameters:**
    - `session_id`: The session ID.
- **Response:**
    - `status`: "ok" if the operation was successful.

### 1.7. `GET /reset`

- **Description:** Resets the current session.
- **Query Parameters:**
    - `session_id`: The session ID.
- **Response:**
    - `status`: "ok" if the operation was successful.

### 1.8. `GET /clear-all`

- **Description:** Clears all session data.
- **Response:**
    - `status`: "ok" if the operation was successful.

### 1.9. `GET /sessions`

- **Description:** Lists all active sessions.
- **Response:**
    - `sessions`: A list of all active sessions.

### 1.10. `GET /followup`

- **Description:** Asks a follow-up question to get more refined suggestions.
- **Query Parameters:**
    - `session_id`: The session ID.
    - `ans` (optional): The user's answer to the follow-up question.
    - `k` (optional): The number of suggestions to return.
- **Response:**
    - `suggestions`: A list of gift suggestions.

## 2. Dependencies

- `fastapi`: For the web server.
- `uvicorn`: For running the FastAPI server.
- `pydantic`: For data validation.
- `main`: For the core logic of the RAG agent.
