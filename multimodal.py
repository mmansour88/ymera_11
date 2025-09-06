from fastapi import APIRouter, UploadFile, File
router = APIRouter()

@router.post("/multimodal/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    content = await audio.read()
    minutes = max(1, len(content) // (16000 * 2 * 60))
    return {"duration_minutes_est": minutes, "transcript": "Transcription placeholder (plug Whisper/Gemini here)"}

@router.post("/multimodal/vision")
async def vision(image: UploadFile = File(...)):
    content = await image.read()
    return {"labels": ["document", "image"], "size": len(content)}
