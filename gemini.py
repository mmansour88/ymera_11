
import os, httpx
from .base import LLMProvider

GEM_URL = os.getenv("GEMINI_BASE_URL","https://generativelanguage.googleapis.com/v1beta/openai")

class GeminiProvider(LLMProvider):
    name = "gemini"
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    async def chat(self, messages, model: str, **kwargs):
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        data = {"model": model, "messages": messages}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{GEM_URL}/chat/completions?key={self.api_key}", json=data)
            r.raise_for_status()
            j = r.json()
            return {
                "content": j["choices"][0]["message"]["content"],
                "usage": j.get("usage", {}),
                "raw": j
            }
