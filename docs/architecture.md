
# Architecture Overview

This document provides a high-level overview of the Slash RAG Agent's architecture.

## 1. System Architecture

The Slash RAG Agent is a web-based application that consists of the following components:

- **FastAPI Server:** A Python web server that exposes the agent's functionality through a RESTful API.
- **RAG Agent:** The core of the application, which is responsible for managing the conversational flow, interacting with the Qdrant vector database, and generating gift suggestions.
- **Qdrant Vector Database:** A vector database that stores the embeddings of the gift experiences.
- **Supabase Database:** A PostgreSQL database that stores the session data.
- **Groq Language Model:** A large language model that is used to generate responses to the user's questions.

## 2. Data Flow

The following diagram illustrates the data flow between the different components of the system:

```mermaid
graph TD
    A[User] --> B(FastAPI Server);
    B --> C{RAG Agent};
    C --> D[Qdrant Vector Database];
    C --> E[Supabase Database];
    C --> F[Groq Language Model];
    F --> C;
    C --> B;
    B --> A;
```

## 3. Execution Flow

The following diagram illustrates the execution flow of the system:

```mermaid
sequenceDiagram
    participant User
    participant FastAPI Server
    participant RAG Agent
    participant Qdrant Vector Database
    participant Supabase Database
    participant Groq Language Model

    User->>FastAPI Server: GET /init
    FastAPI Server->>RAG Agent: get_question()
    RAG Agent->>Groq Language Model: query_groq()
    Groq Language Model-->>RAG Agent: response
    RAG Agent-->>FastAPI Server: question
    FastAPI Server-->>User: question

    User->>FastAPI Server: POST /submit
    FastAPI Server->>RAG Agent: get_ans()
    RAG Agent->>Supabase Database: save_session_to_db()
    Supabase Database-->>RAG Agent: response
    RAG Agent-->>FastAPI Server: status
    FastAPI Server-->>User: status

    User->>FastAPI Server: GET /suggestion
    FastAPI Server->>RAG Agent: get_top_chunks()
    RAG Agent->>Qdrant Vector Database: query_points()
    Qdrant Vector Database-->>RAG Agent: chunks
    RAG Agent-->>FastAPI Server: suggestions
    FastAPI Server-->>User: suggestions
```
