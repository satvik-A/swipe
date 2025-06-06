from langchain_core.language_models.llms import LLM
from typing import Optional, List
from tools import query_groq

class GroqLLM(LLM):
    model: str = "llama3-8b-8192"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return query_groq([{"role": "user", "content": prompt}], self.model)

    @property
    def _llm_type(self) -> str:
        return "groq"