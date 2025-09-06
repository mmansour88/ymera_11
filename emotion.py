from fastapi import APIRouter, Body

router = APIRouter()

@router.post("/emotion/style")
def style(text: str = Body(..., embed=True)):
    t = text.lower()
    if any(w in t for w in ["error","fail","angry","bad"]):
        return {"tone": "calm_reassuring", "suggestion": "Acknowledge frustration, propose next steps."}
    if any(w in t for w in ["great","love","awesome","good"]):
        return {"tone": "enthusiastic", "suggestion": "Celebrate progress, encourage momentum."}
    return {"tone": "neutral", "suggestion": "Be clear and concise."}
