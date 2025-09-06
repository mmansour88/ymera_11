
import os, httpx, asyncio
from .base import LLMProvider

OPENAI_URL = os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1")

class OpenAIProvider(LLMProvider):
    name = "openai"
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    async def chat(self, messages, model: str, **kwargs):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        data = {"model": model, "messages": messages, "temperature": kwargs.get("temperature", 0.2)}
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{OPENAI_URL}/chat/completions", json=data, headers={"Authorization": f"Bearer {self.api_key}"})
            r.raise_for_status()
            j = r.json()
            return {
                "content": j["choices"][0]["message"]["content"],
                "usage": j.get("usage", {}),
                "raw": j
            }
