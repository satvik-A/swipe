
# `main.py`

This file contains the core logic for the Slash RAG Agent. It manages the conversational flow, interacts with the Qdrant vector database, and generates gift suggestions.

## 1. Functions

### 1.1. `get_question(session_id)`

- **Description:** Gets the next question to ask the user.
- **Parameters:**
    - `session_id`: The session ID.
- **Returns:** The next question to ask the user.

### 1.2. `get_ans(session_id, ans)`

- **Description:** Submits an answer to the current question.
- **Parameters:**
    - `session_id`: The session ID.
    - `ans`: The user's answer to the question.
- **Returns:** The key under which the answer was stored.

### 1.3. `get_top_chunks(query, k=5)`

- **Description:** Retrieves the most relevant chunks from Qdrant.
- **Parameters:**
    - `query`: The query to search for.
    - `k` (optional): The number of chunks to return.
- **Returns:** A list of the most relevant chunks.

### 1.4. `go_back(session_id)`

- **Description:** Goes back to the previous question.
- **Parameters:**
    - `session_id`: The session ID.

### 1.5. `reset_session(session_id)`

- **Description:** Resets the current session.
- **Parameters:**
    - `session_id`: The session ID.

### 1.6. `clear_all_sessions()`

- **Description:** Clears all session data.

### 1.7. `get_all_sessions()`

- **Description:** Returns a list of all active sessions.

### 1.8. `follow_up_chat(session_id, ans, k=12)`

- **Description:** Asks a follow-up question to get more refined suggestions.
- **Parameters:**
    - `session_id`: The session ID.
    - `ans`: The user's answer to the follow-up question.
    - `k` (optional): The number of suggestions to return.
- **Returns:** A list of gift suggestions.

## 2. Dependencies

- `tools`: For helper functions for external APIs (Groq, DDG, Wikipedia).
- `qdrant-client`: For interacting with the Qdrant vector database.
- `openai`: For using Azure OpenAI embeddings.
- `supabase`: For database interactions.
- `python-dotenv`: For managing environment variables.
