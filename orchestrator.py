
import os, json, httpx, asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from .models import Agent, Task, Report, Policy, ToolUseLog
from .db import SessionLocal
from .integrations.llm_providers import smart_chat, LLMError
import os
from .tools_registry import TOOLS
from .budgets import check_and_increment
from .alerts import send_alert

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Slack/Discord/Custom
WEBHOOK_ERR  = os.getenv("WEBHOOK_ERROR_URL", WEBHOOK_URL)

async def post_webhook(payload: Dict[str,Any], error: bool=False):
    url = WEBHOOK_ERR if error else WEBHOOK_URL
    if not url: return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json=payload)
    except Exception:
        pass

async def run_agent_task(agent_id: int, task_id: int) -> Dict[str,Any]:
    # Basic policy + budget + tool-use aware runner
    db: Session = SessionLocal()
    try:
        agent = db.query(Agent).get(agent_id)
        task  = db.query(Task).get(task_id)
        if not agent or not task:
            return {"error":"agent or task missing"}

        # Example: policy check (auto-assign off?)
        pol = db.query(Policy).filter(Policy.name=="auto_assign").first()
        if pol and not pol.enabled:
            return {"status":"skipped_by_policy"}

        # Budget check for provider (if stored in agent.specialization as provider name)
        provider = (agent.specialization or "anthropic").lower()
        ok, budget = check_and_increment(db, provider)
        if not ok:
            await post_webhook({"type":"budget_exceeded", "provider": provider, "task": task_id}, error=True)
            return {"error":"budget_exceeded","provider":provider}

        # Compose prompt and allow minimal tool hints
        messages = [{"role":"user","content": f"Task: {task.title}\n{task.description}\nUse tools if needed."}]
        try:
            output = await smart_chat(provider, messages)
        except LLMError as e:
            await post_webhook({"type":"llm_error","provider":provider,"err":str(e)}, error=True)
            # fallback order (env-driven)
            order = os.getenv("PROVIDER_ORDER","groq,anthropic,openai,deepseek,gemini").split(",")
            for alt in order:
                if alt==provider: continue
                try:
                    output = await smart_chat(alt, messages)
                    provider = alt
                    break
                except LLMError:
                    continue
            else:
                return {"error":"all_providers_failed"}

        # Log a simple report
        rep = Report(task_id=task.id, agent_id=agent.id, flag="green", notes=output[:5000])  # auto-lockdown

# Simple heuristic: if output mentions 'security breach' → red
if 'security breach' in (output or '').lower():
    rep.flag = 'red'
db.add(rep); db.flush()
if rep.flag == 'red':
    # Pause all teams containing this agent (if TeamAgents table exists, we assume simple Team table with head link)
    try:
        # We don't know schema for memberships; we mark any team with head_agent_id
        from .models import Team
        teams = db.query(Team).filter((Team.head_agent_id==agent.id) | (Team.head_agent_id==agent.id)).all()
        for t in teams:
            t.paused = True
            db.add(t)
        await post_webhook({"type":"red_flag_lockdown","task":task.id,"agent":agent.id}, error=True)
        await send_alert("YMERA: RED FLAG LOCKDOWN", f"Agent {agent.id} triggered red flag on task {task.id}. Teams paused.")
    except Exception:
        pass

        await post_webhook({"type":"task_complete","task":task.id,"agent":agent.id,"flag":rep.flag})
        db.commit()
        return {"ok": True, "report_id": rep.id, "provider": provider}
    finally:
        db.close()

async def use_tool(agent_id: Optional[int], tool: str, params: Dict[str,Any]):
    func = TOOLS.get(tool)
    if not func:
        return {"error":"tool_not_found"}
    out = await func(params)
    # log it
    db = SessionLocal()
    try:
        log = ToolUseLog(agent_id=agent_id, tool=tool, input=params, output=out)
        db.add(log); db.commit()
    finally:
        db.close()
    return out
