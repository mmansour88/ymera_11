
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import base64, os, httpx
from .integrations.llm_providers import smart_chat
from .guardrails import sanitize_prompt
from .quotas import check_and_inc_user_quota
from .db import get_db, LLMError

router = APIRouter(prefix="/models", tags=["models"])

class Msg(BaseModel):
    role: str
    content: str

class ChatIn(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    messages: List[Msg]

@router.post("/chat")
async def chat(payload: ChatIn):
    try:
        text = await smart_chat(payload.provider or "", [m.model_dump() for m in payload.messages], model=payload.model)
        return {"ok": True, "output": text}
    except LLMError as e:
        raise HTTPException(400, str(e))

@router.post("/vision")
async def vision_qna(
    prompt: str = Form(...),
    provider: Optional[str] = Form(None),
    image: UploadFile = File(...),
):
    # Basic OpenAI-compatible vision if using OpenAI; else failover to Gemini (not streaming here)
    data = await image.read()
    b64 = base64.b64encode(data).decode()
    oai_key = os.getenv("OPENAI_API_KEY")
    if oai_key:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {oai_key}"},
                json={
                    "model": os.getenv("OPENAI_VISION_MODEL","gpt-4o-mini"),
                    "messages":[{
                        "role":"user",
                        "content":[
                            {"type":"text","text": prompt},
                            {"type":"image_url","image_url":{"url": f"data:{image.content_type};base64,{b64}" }}
                        ]
                    }]
                }
            )
            if r.status_code >= 400:
                raise HTTPException(400, f"OpenAI vision error: {r.text}")
            return {"ok": True, "output": r.json()["choices"][0]["message"]["content"]}
    # Gemini Vision
    gkey = os.getenv("GOOGLE_API_KEY")
    if gkey:
        async with httpx.AsyncClient(timeout=90) as client:
            model = os.getenv("GEMINI_VISION_MODEL","gemini-1.5-flash")
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gkey}",
                json={
                    "contents":[{
                        "role":"user",
                        "parts":[
                            {"text": prompt},
                            {"inline_data": {"mime_type": image.content_type, "data": b64}}
                        ]
                    }]
                }
            )
            if r.status_code >= 400:
                raise HTTPException(400, f"Gemini vision error: {r.text}")
            data = r.json()
            return {"ok": True, "output": data["candidates"][0]["content"]["parts"][0]["text"]}
    raise HTTPException(400, "No vision-capable provider configured")

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # OpenAI Whisper-style
    oai_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("WHISPER_MODEL","whisper-1")
    if not oai_key:
        raise HTTPException(400, "OPENAI_API_KEY missing")
    async with httpx.AsyncClient(timeout=90) as client:
        # Use multipart form-data per OpenAI spec
        files = {'file': (file.filename, await file.read(), file.content_type)}
        data = {'model': model}
        r = await client.post("https://api.openai.com/v1/audio/transcriptions",
                              headers={"Authorization": f"Bearer {oai_key}"}, files=files, data=data)
        if r.status_code >= 400:
            raise HTTPException(400, f"Transcription error: {r.text}")
        return {"ok": True, "text": r.json().get("text","")}
