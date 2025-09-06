import os, httpx, hashlib, numpy as np
from typing import List

def _local_embed(text: str) -> List[float]:
    vec = np.zeros(256, dtype=np.float32)
    for ch in text.lower():
        vec[ord(ch) % 256] += 1.0
    n = np.linalg.norm(vec) or 1.0
    return (vec / n).tolist()

async def _openai_embed(text: str):
    key = os.getenv("OPENAI_API_KEY")
    if not key: return None
    url = "https://api.openai.com/v1/embeddings"
    async with httpx.AsyncClient(timeout=20) as cx:
        r = await cx.post(url, headers={"Authorization": f"Bearer {key}"}, json={"model":"text-embedding-3-small","input": text})
        if r.status_code >= 400: return None
        data = r.json()
        return data["data"][0]["embedding"]

async def _gemini_embed(text: str):
    key = os.getenv("GEMINI_API_KEY")
    if not key: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedText?key={key}"
    async with httpx.AsyncClient(timeout=20) as cx:
        r = await cx.post(url, json={"text": text})
        if r.status_code >= 400: return None
        data = r.json()
        values = data.get("embedding",{}).get("value",[])
        return values or None

async def embed(text: str) -> List[float]:
    # Fallback chain: OpenAI -> Gemini -> Local
    for fn in (_openai_embed, _gemini_embed):
        try:
            v = await fn(text)
            if v: return v
        except Exception:
            continue
    return _local_embed(text)
