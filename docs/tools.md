
# `tools.py`

This file contains helper functions for interacting with external APIs, such as Groq, DuckDuckGo, and Wikipedia.

## 1. Functions

### 1.1. `query_groq(messages, model="llama3-8b-8192")`

- **Description:** Queries the Groq API to get a response from the language model.
- **Parameters:**
    - `messages`: A list of messages to send to the language model.
    - `model` (optional): The language model to use.
- **Returns:** The response from the language model.

### 1.2. `search_ddg(query, max_results=5)`

- **Description:** Searches DuckDuckGo for the given query.
- **Parameters:**
    - `query`: The query to search for.
    - `max_results` (optional): The maximum number of results to return.
- **Returns:** A list of search results.

### 1.3. `search_wikipedia(query, sentences=2)`

- **Description:** Searches Wikipedia for the given query.
- **Parameters:**
    - `query`: The query to search for.
    - `sentences` (optional): The number of sentences to return.
- **Returns:** The summary of the Wikipedia page.

### 1.4. `search_online(query)`

- **Description:** Searches both DuckDuckGo and Wikipedia for the given query.
- **Parameters:**
    - `query`: The query to search for.
- **Returns:** A dictionary containing the search results from both DuckDuckGo and Wikipedia.

## 2. Dependencies

- `requests`: For making HTTP requests.
- `python-dotenv`: For managing environment variables.
- `duckduckgo_search`: For searching DuckDuckGo.
- `wikipedia`: For searching Wikipedia.
