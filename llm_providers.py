
import os, httpx, base64, json
from typing import Optional, List, Dict, Any

TIMEOUT = 90

class LLMError(Exception):
    pass

def _client():
    return httpx.AsyncClient(timeout=TIMEOUT)

# --- OpenAI-compatible (OpenAI/Groq/DeepSeek that expose OpenAI schema) ---
async def openai_chat(messages: List[Dict[str, str]], model: Optional[str]=None, base_url: Optional[str]=None, api_key: Optional[str]=None) -> str:
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY missing")
    base = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages}
    async with _client() as client:
        r = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
        if r.status_code >= 400:
            raise LLMError(f"OpenAI error {r.status_code}: {r.text}")
        data = r.json()
        return data["choices"][0]["message"]["content"]

async def groq_chat(messages: List[Dict[str,str]], model: Optional[str]=None) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise LLMError("GROQ_API_KEY missing")
    base = "https://api.groq.com/openai/v1"
    model = model or "llama-3.3-70b-versatile"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages}
    async with _client() as client:
        r = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
        if r.status_code >= 400:
            raise LLMError(f"Groq error {r.status_code}: {r.text}")
        return r.json()["choices"][0]["message"]["content"]

async def deepseek_chat(messages: List[Dict[str,str]], model: Optional[str]=None) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise LLMError("DEEPSEEK_API_KEY missing")
    base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = model or "deepseek-chat"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages}
    async with _client() as client:
        r = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
        if r.status_code >= 400:
            raise LLMError(f"DeepSeek error {r.status_code}: {r.text}")
        return r.json()["choices"][0]["message"]["content"]

# --- Anthropic ---
async def anthropic_chat(messages: List[Dict[str, str]], model: Optional[str]=None, system: Optional[str]=None) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY missing")
    model = model or os.getenv("ANTHROPIC_MODEL","claude-3-5-sonnet-20241022")
    # Convert to Anthropic message format
    content = [{"role": m["role"], "content": m["content"]} for m in messages if m["role"] in ("user","assistant")]
    async with _client() as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "system": system or os.getenv("ANTHROPIC_SYSTEM",""),
                "max_tokens": 1024,
                "messages": content
            }
        )
        if r.status_code >= 400:
            raise LLMError(f"Anthropic error {r.status_code}: {r.text}")
        data = r.json()
        # concat text blocks
        texts = []
        for blk in data.get("content", []):
            if blk.get("type") == "text":
                texts.append(blk.get("text",""))
        return "\n".join(texts)

# --- Google Gemini ---
async def gemini_chat(messages: List[Dict[str,str]], model: Optional[str]=None) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise LLMError("GOOGLE_API_KEY missing")
    model = model or os.getenv("GEMINI_MODEL","gemini-1.5-flash")
    # Simplified text-only; for vision use /vision endpoint
    history = [{"role": "user" if m["role"]=="user" else "model", "parts":[{"text": m["content"]}]} for m in messages]
    async with _client() as client:
        r = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            json={"contents": history}
        )
        if r.status_code >= 400:
            raise LLMError(f"Gemini error {r.status_code}: {r.text}")
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

# --- Simple provider router ---
async def smart_chat(provider: str, messages: List[Dict[str,str]], model: Optional[str]=None) -> str:
    p = (provider or "").lower()
    if p in ("openai","oai"):
        return await openai_chat(messages, model=model)
    if p in ("anthropic","claude"):
        return await anthropic_chat(messages, model=model)
    if p == "groq":
        return await groq_chat(messages, model=model)
    if p == "deepseek":
        return await deepseek_chat(messages, model=model)
    if p in ("gemini","google"):
        return await gemini_chat(messages, model=model)
    # auto priority
    for try_p in ("anthropic","openai","groq","deepseek","gemini"):
        try:
            return await smart_chat(try_p, messages, model)
        except LLMError:
            continue
    raise LLMError("No providers configured")
