
import os, httpx
from .base import LLMProvider

ANTH_URL = os.getenv("ANTHROPIC_BASE_URL","https://api.anthropic.com/v1/messages")

class AnthropicProvider(LLMProvider):
    name = "anthropic"
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    async def chat(self, messages, model: str, **kwargs):
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        content = []
        for m in messages:
            role = m.get("role","user")
            if role == "system":
                # Anthropic uses system in top-level param; merge prompt at front
                continue
            content.append({"role": role, "content": m["content"]})
        data = {"model": model, "max_tokens": kwargs.get("max_tokens", 1024), "messages": content, "system": next((m["content"] for m in messages if m["role"]=="system"), None)}
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(ANTH_URL, json=data, headers=headers)
            r.raise_for_status()
            j = r.json()
            return {
                "content": j["content"][0]["text"] if j.get("content") else "",
                "usage": j.get("usage", {}),
                "raw": j
            }
