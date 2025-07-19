
# `swipe.py`

This file contains the core logic for the swipe feature. It interacts with the Qdrant vector database to get recommendations based on user preferences.

## 1. Functions

### 1.1. `get_top_chunks(query, k=5)`

- **Description:** Retrieves the most relevant chunks from Qdrant.
- **Parameters:**
    - `query`: The query to search for.
    - `k` (optional): The number of chunks to return.
- **Returns:** A list of the most relevant chunks.

## 2. Dependencies

- `tools`: For helper functions for external APIs (Groq, DDG, Wikipedia).
- `qdrant-client`: For interacting with the Qdrant vector database.
- `openai`: For using Azure OpenAI embeddings.
- `supabase`: For database interactions.
- `python-dotenv`: For managing environment variables.
