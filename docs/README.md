
# Slash RAG Agent Documentation

Welcome to the developer documentation for the Slash RAG Agent. This document provides a comprehensive overview of the project, its architecture, and its components.

## 1. Project Overview

The Slash RAG Agent is a personalized experience gift suggestion agent. It uses a Retrieval Augmented Generation (RAG) architecture to provide tailored gift recommendations based on user input. The agent interacts with users through a conversational interface, asking a series of questions to understand the recipient's preferences, the occasion, and the user's budget.

### 1.1. Features

- **Conversational AI:** Engages users in a natural conversation to gather information.
- **Personalized Suggestions:** Provides gift ideas tailored to the recipient's interests.
- **RAG Architecture:** Utilizes a Qdrant vector database to retrieve relevant experiences and Groq for generating responses.
- **Session Management:** Supports multiple users with session tracking.
- **Supabase Integration:** Persists session data in a Supabase database.
- **FastAPI Server:** Exposes the agent's functionality through a RESTful API.

### 1.2. How It Works

1.  **Initiation:** The user starts a session by sending a request to the `/init` endpoint.
2.  **Questioning:** The agent asks a series of questions to gather context about the gift recipient.
3.  **Answer Submission:** The user submits answers to the questions.
4.  **Context Building:** The agent builds a context profile based on the user's answers.
5.  **Suggestion Generation:** The agent uses the context to query the Qdrant vector database for relevant experiences.
6.  **Response Generation:** The retrieved experiences are fed to the Groq language model to generate a final, user-friendly suggestion.
7.  **Follow-up:** The user can ask follow-up questions to refine the suggestions.

## 2. Getting Started

### 2.1. Prerequisites

- Python 3.10+
- Pip
- Virtualenv (recommended)

### 2.2. Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/slash-rag-agent.git
    cd slash-rag-agent
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv slash
    source slash/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root of the project and add the following variables:

    ```
    GROQ_API_KEY="your_groq_api_key"
    AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
    AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint"
    QDRANT_API_KEY="your_qdrant_api_key"
    QDRANT_HOST="your_qdrant_host"
    SUPABASE_URL="your_supabase_url"
    SUPABASE_KEY="your_supabase_key"
    ```

## 3. Usage

### 3.1. Running the API Server

To start the FastAPI server, run the following command:

```bash
uvicorn api_server:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 3.2. API Endpoints

- `GET /init`: Initializes a new session and returns the first question.
- `POST /submit`: Submits an answer to the current question.
- `GET /next`: Retrieves the next question in the sequence.
- `GET /suggestion`: Gets gift suggestions based on the current context.
- `GET /context`: Returns the current session's context.
- `GET /back`: Goes back to the previous question.
- `GET /reset`: Resets the current session.
- `GET /clear-all`: Clears all session data.
- `GET /sessions`: Lists all active sessions.
- `GET /followup`: Asks a follow-up question to get more refined suggestions.

### 3.3. Running the CLI

You can also interact with the agent through the command line:

```bash
python main.py
```

## 4. Project Structure

```
.
├── api_server.py         # FastAPI application
├── main.py               # Core logic for the RAG agent
├── tools.py              # Helper functions for external APIs (Groq, DDG, Wikipedia)
├── perplexity_llm.py     # (Not fully integrated) Perplexity API integration
├── requirements.txt      # Project dependencies
└── slash/                  # Virtual environment
```

## 5. Dependencies

The main dependencies are listed in `requirements.txt` and include:

- `fastapi`: For the web server.
- `uvicorn`: For running the FastAPI server.
- `qdrant-client`: For interacting with the Qdrant vector database.
- `openai`: For using Azure OpenAI embeddings.
- `supabase`: For database interactions.
- `python-dotenv`: For managing environment variables.
- `groq`: For accessing the Groq API.

## 6. License

This project is licensed under the MIT License. See the `LICENSE` file for details.
