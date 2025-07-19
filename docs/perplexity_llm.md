
# `perplexity_llm.py`

This file contains a wrapper for the Groq language model, allowing it to be used as a LangChain LLM.

## 1. Classes

### 1.1. `GroqLLM`

- **Description:** A LangChain LLM wrapper for the Groq language model.
- **Methods:**
    - `_call(prompt, stop=None)`: Calls the Groq API to get a response from the language model.
    - `_llm_type()`: Returns the type of the LLM.

## 2. Dependencies

- `langchain_core`: For the `LLM` class.
- `tools`: For the `query_groq` function.
