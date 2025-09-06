
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .db import get_db
from .models import Policy, Budget, Agent, Task, UserQuota, UserProviderQuota, AgentProfile, ToolUseLog, Report
from .rbac import require_role
from .orchestrator import run_agent_task, use_tool

router = APIRouter(prefix="/control", tags=["control"])

class PolicyIn(BaseModel):
    name: str
    enabled: bool
    data: Optional[Dict[str,Any]] = None

@router.post("/policy", dependencies=[Depends(require_role("admin","manager"))])
def set_policy(p: PolicyIn, db: Session = Depends(get_db)):
    pol = db.query(Policy).filter(Policy.name==p.name).first()
    if not pol:
        pol = Policy(name=p.name, enabled=p.enabled, data=p.data or {})
    else:
        pol.enabled = p.enabled
        pol.data = p.data or {}
    db.add(pol); db.commit()
    return {"ok": True}

class BudgetIn(BaseModel):
    provider: str
    daily_limit_usd: float

@router.post("/budget", dependencies=[Depends(require_role("admin","manager"))])
def set_budget(b: BudgetIn, db: Session = Depends(get_db)):
    row = db.query(Budget).filter(Budget.provider==b.provider.lower()).first()
    if not row:
        row = Budget(provider=b.provider.lower(), daily_limit_usd=b.daily_limit_usd, spent_today_usd=0.0)
    else:
        row.daily_limit_usd = b.daily_limit_usd
    db.add(row); db.commit()
    return {"ok": True}

class RunIn(BaseModel):
    agent_id: int
    task_id: int

@router.post("/run", dependencies=[Depends(require_role("admin","manager"))])
async def run_once(payload: RunIn):
    return await run_agent_task(payload.agent_id, payload.task_id)

class ToolIn(BaseModel):
    agent_id: Optional[int] = None
    tool: str
    params: Dict[str,Any]

@router.post("/tool", dependencies=[Depends(require_role("admin","manager","operator"))])
async def run_tool(payload: ToolIn):
    return await use_tool(payload.agent_id, payload.tool, payload.params)


class QuotaIn(BaseModel):
    user_id: int
    daily_calls: int

@router.post("/quota", dependencies=[Depends(require_role("admin","manager"))])
def set_quota(q: QuotaIn, db: Session = Depends(get_db)):
    row = db.query(UserQuota).filter(UserQuota.user_id==q.user_id).first()
    if not row:
        row = UserQuota(user_id=q.user_id, daily_calls=q.daily_calls, used_today=0)
    else:
        row.daily_calls = q.daily_calls
    db.add(row); db.commit()
    return {"ok": True}


class ProviderQuotaIn(BaseModel):
    user_id: int
    provider: str
    daily_calls: int

@router.post("/quota/provider", dependencies=[Depends(require_role("admin","manager"))])
def set_provider_quota(p: ProviderQuotaIn, db: Session = Depends(get_db)):
    row = db.query(UserProviderQuota).filter(UserProviderQuota.user_id==p.user_id, UserProviderQuota.provider==p.provider.lower()).first()
    if not row:
        row = UserProviderQuota(user_id=p.user_id, provider=p.provider.lower(), daily_calls=p.daily_calls, used_today=0)
    else:
        row.daily_calls = p.daily_calls
    db.add(row); db.commit()
    return {"ok": True}

@router.post("/agent/{agent_id}/avatar", dependencies=[Depends(require_role("admin","manager"))])
def upload_avatar(agent_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(('.glb','.gltf','.png','.jpg','.jpeg','.webp')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    up_dir = os.getenv("UPLOAD_DIR", "/data/uploads")
    os.makedirs(up_dir, exist_ok=True)
    path = os.path.join(up_dir, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    prof = db.query(AgentProfile).filter(AgentProfile.agent_id==agent_id).first()
    if not prof:
        prof = AgentProfile(agent_id=agent_id, avatar_url=path)
    else:
        prof.avatar_url = path
    db.add(prof); db.commit()
    return {"ok": True, "avatar_url": path}

@router.get("/export/audit", dependencies=[Depends(require_role("admin","manager"))])
def export_audit(db: Session = Depends(get_db)):
    logs = db.query(ToolUseLog).all()
    reps = db.query(Report).all()
    import io, csv, base64
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["type","id","agent_id","tool","input","output","task_id","flag","notes"])
    for l in logs:
        w.writerow(["tool", l.id, l.agent_id, l.tool, json.dumps(l.input), json.dumps(l.output), "", "", ""])
    for r in reps:
        w.writerow(["report", r.id, r.agent_id, "", "", "", r.task_id, r.flag, (r.notes or "")[:2000]])
    data = buf.getvalue()
    # Optional: email as attachment link not implemented in Mailgun helper; return inline data
    return {"csv": data}
