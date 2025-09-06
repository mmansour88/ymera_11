
import os, httpx
from .base import LLMProvider

GROQ_URL = os.getenv("GROQ_BASE_URL","https://api.groq.com/openai/v1")

class GroqProvider(LLMProvider):
    name = "groq"
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    async def chat(self, messages, model: str, **kwargs):
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        data = {"model": model, "messages": messages, "temperature": kwargs.get("temperature", 0.2)}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{GROQ_URL}/chat/completions", json=data, headers={"Authorization": f"Bearer {self.api_key}"})
            r.raise_for_status()
            j = r.json()
            return {
                "content": j["choices"][0]["message"]["content"],
                "usage": j.get("usage", {}),
                "raw": j
            }
