import os, base64, json, httpx

class ProviderError(Exception): ...

def _get(name, default=None): return os.getenv(name, default)

class AnthropicClient:
    def __init__(self):
        self.key = _get("ANTHROPIC_API_KEY")
        self.base = _get("ANTHROPIC_API_BASE","https://api.anthropic.com")
        self.model = _get("ANTHROPIC_MODEL","claude-3-5-sonnet-20240620")
        self.version = "2023-06-01"
    async def chat(self, system:str, messages:list, max_tokens:int=2048):
        if not self.key: raise ProviderError("Missing ANTHROPIC_API_KEY")
        url = f"{self.base}/v1/messages"
        headers = {"x-api-key": self.key, "anthropic-version": self.version, "content-type":"application/json"}
        payload = {"model": self.model, "system": system, "messages": messages, "max_tokens": max_tokens}
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data

class OpenAIClient:
    def __init__(self):
        self.key = _get("OPENAI_API_KEY")
        self.base = _get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.chat_model = _get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        self.audio_model = _get("OPENAI_WHISPER_MODEL", "whisper-1")
        self.vision_model = _get("OPENAI_VISION_MODEL", "gpt-4o-mini")
    async def chat(self, messages:list, max_tokens:int=2048):
        if not self.key: raise ProviderError("Missing OPENAI_API_KEY")
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {"model": self.chat_model, "messages": messages, "max_tokens": max_tokens}
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, headers=headers, json=payload)
            r.raise_for_status(); return r.json()
    async def transcribe(self, filename:str, content:bytes):
        if not self.key: raise ProviderError("Missing OPENAI_API_KEY")
        url = f"{self.base}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.key}"}
        files = {"file": (filename, content), "model": (None, self.audio_model)}
        async with httpx.AsyncClient(timeout=300) as cx:
            r = await cx.post(url, headers=headers, files=files)
            r.raise_for_status(); return r.json()
    async def vision(self, prompt:str, filename:str, content:bytes):
        if not self.key: raise ProviderError("Missing OPENAI_API_KEY")
        b64 = base64.b64encode(content).decode()
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {
            "model": self.vision_model,
            "messages":[{"role":"user","content":[
                {"type":"text","text":prompt},
                {"type":"image_url","image_url":{"url": f"data:application/octet-stream;base64,{b64}" }}
            ]}]
        }
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, headers=headers, json=payload)
            r.raise_for_status(); return r.json()

class GroqClient:
    def __init__(self):
        self.key = _get("GROQ_API_KEY")
        self.base = _get("GROQ_API_BASE","https://api.groq.com/openai/v1")
        self.model = _get("GROQ_MODEL","llama-3.3-70b-versatile")
    async def chat(self, messages:list, max_tokens:int=2048):
        if not self.key: raise ProviderError("Missing GROQ_API_KEY")
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {"model": self.model, "messages": messages, "max_tokens": max_tokens}
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, headers=headers, json=payload)
            r.raise_for_status(); return r.json()

class DeepSeekClient:
    def __init__(self):
        self.key = _get("DEEPSEEK_API_KEY")
        self.base = _get("DEEPSEEK_API_BASE","https://api.deepseek.com")
        self.model = _get("DEEPSEEK_MODEL","deepseek-chat")
    async def chat(self, messages:list, max_tokens:int=2048):
        if not self.key: raise ProviderError("Missing DEEPSEEK_API_KEY")
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {"model": self.model, "messages": messages, "max_tokens": max_tokens}
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, headers=headers, json=payload)
            r.raise_for_status(); return r.json()

class GeminiClient:
    def __init__(self):
        self.key = _get("GEMINI_API_KEY")
        self.base = _get("GEMINI_API_BASE","https://generativelanguage.googleapis.com")
        self.model = _get("GEMINI_MODEL","gemini-1.5-flash")
    async def chat(self, messages:list, system:str|None=None, max_output_tokens:int=2048):
        if not self.key: raise ProviderError("Missing GEMINI_API_KEY")
        url = f"{self.base}/v1beta/models/{self.model}:generateContent?key={self.key}"
        parts = []
        if system: parts.append({"text": f"[SYSTEM]\n{system}"})
        for m in messages:
            parts.append({"text": f"[{m['role'].upper()}]\n{m['content']}"})
        payload = {"contents":[{"parts":[ {"text": p["text"]} for p in parts ]}], "generationConfig": {"maxOutputTokens": max_output_tokens}}
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, json=payload)
            r.raise_for_status(); return r.json()

def choose_clients():
    return {
        "anthropic": AnthropicClient() if os.getenv("ANTHROPIC_API_KEY") else None,
        "openai": OpenAIClient() if os.getenv("OPENAI_API_KEY") else None,
        "groq": GroqClient() if os.getenv("GROQ_API_KEY") else None,
        "deepseek": DeepSeekClient() if os.getenv("DEEPSEEK_API_KEY") else None,
        "gemini": GeminiClient() if os.getenv("GEMINI_API_KEY") else None,
    }
