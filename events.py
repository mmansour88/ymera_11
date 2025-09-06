import httpx, asyncio, hashlib, hmac, os, json
from typing import List, Dict

SUBSCRIBERS: Dict[str, List[dict]] = {}  # topic -> [{url, secret}]

def subscribe(topic: str, url: str, secret: str | None):
    SUBSCRIBERS.setdefault(topic, []).append({"url": url, "secret": secret})

def unsubscribe(topic: str, url: str):
    SUBSCRIBERS[topic] = [s for s in SUBSCRIBERS.get(topic, []) if s["url"] != url]

async def publish(topic: str, event: dict):
    payload = json.dumps(event)
    async with httpx.AsyncClient(timeout=10) as cx:
        tasks = []
        for s in SUBSCRIBERS.get(topic, []):
            sig = None
            if s.get("secret"):
                sig = hmac.new(s["secret"].encode(), payload.encode(), hashlib.sha256).hexdigest()
            headers = {"Content-Type": "application/json"}
            if sig: headers["X-YMERA-Signature"] = sig
            tasks.append(cx.post(s["url"], headers=headers, content=payload))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
