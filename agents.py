
import asyncio
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..services.governance import is_team_suspended
from ..services.budgets import enforce_budget, add_usage
from decimal import Decimal, Depends, HTTPException
from pydantic import BaseModel
from ..auth.rbac import require_scope, TokenPayload
from ..services.budgets import add_usage, enforce_budget
from ..services.router import pick_provider_and_model
from ..db import get_db
from sqlalchemy.orm import Session

from ..providers.openai import OpenAIProvider
from ..providers.anthropic import AnthropicProvider
from ..providers.groq import GroqProvider
from ..providers.deepseek import DeepseekProvider
from ..providers.gemini import GeminiProvider

router = APIRouter()

providers = {
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
    "groq": GroqProvider(),
    "deepseek": DeepseekProvider(),
    "gemini": GeminiProvider(),
}

class AgentTaskRequest(BaseModel):
    task_type: str = "general"
    desired_quality: str = "balanced"
    messages: list[dict]
    model: str | None = None
    provider: str | None = None

@router.post("/run")
async def run_task(req: AgentTaskRequest, auth: TokenPayload = Depends(require_scope("agents:run")), db: Session = Depends(get_db)):
    enforce_budget(auth.org_id, db)

    provider_name, model = pick_provider_and_model(req.task_type, req.desired_quality)
    if req.provider: provider_name = req.provider
    if req.model: model = req.model
    prov = providers.get(provider_name)
    if not prov:
        raise HTTPException(400, f"unknown provider {provider_name}")

    result = await prov.chat(req.messages, model=model)
    usage = result.get("usage", {})
    in_toks = int(usage.get("prompt_tokens", 500))
    out_toks = int(usage.get("completion_tokens", 1000))
    # rough cost
    cost = Decimal(prov.estimate_cost(in_toks, out_toks, model)).quantize(Decimal("0.000001"))
    add_usage(db, org_id=auth.org_id, usd=cost, tokens_in=in_toks, tokens_out=out_toks)
    return {"provider": provider_name, "model": model, "content": result["content"], "usage": usage, "cost_usd": str(cost)}
