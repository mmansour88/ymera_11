from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..db import get_db, Base, engine
from ..models import User, Project, FileAsset, Room, Report, Rating
from ..utils.auth import create_pair, verify_token, revoke_token, hash_password, verify_password
from ..utils.ws import hub
import base64

router = APIRouter()

Base.metadata.create_all(bind=engine)

@router.post("/auth/register")
def register(email: str, name: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(400, "Email already exists")
    u = User(email=email, name=name, password_hash=hash_password(password))
    db.add(u); db.commit()
    return {"id": u.id, "email": email}

@router.post("/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    u = db.query(User).filter_by(email=email).first()
    if not u or not verify_password(password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return create_pair(sub=str(u.id), roles=["admin"] if u.is_admin else ["user"], session_id="sid")

@router.get("/auth/verify")
def verify(token: str, db: Session = Depends(get_db)):
    return verify_token(token, db)

@router.post("/auth/revoke")
def revoke(token: str, db: Session = Depends(get_db)):
    revoke_token(token, db); return {"status": "revoked"}

@router.post("/projects")
def create_project(owner_id: int, name: str, desc: str = "", db: Session = Depends(get_db)):
    p = Project(owner_id=owner_id, name=name, desc=desc); db.add(p); db.commit(); return {"id": p.id}

@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return [{"id": p.id, "name": p.name, "owner_id": p.owner_id} for p in db.query(Project).all()]

@router.post("/files/upload")
async def upload_file(project_id: int, f: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await f.read()
    fa = FileAsset(project_id=project_id, name=f.filename, mime=f.content_type, content=content)
    db.add(fa); db.commit()
    return {"id": fa.id, "name": fa.name}

@router.get("/files/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    fa = db.query(FileAsset).get(file_id)
    if not fa: raise HTTPException(404, "Not found")
    return {"filename": fa.name, "mime": fa.mime, "base64": base64.b64encode(fa.content).decode()}

@router.post("/files/edit/{file_id}")
def edit_file(file_id: int, text: str, db: Session = Depends(get_db)):
    fa = db.query(FileAsset).get(file_id)
    if not fa: raise HTTPException(404, "Not found")
    fa.content = text.encode(); db.commit()
    return {"ok": True}

@router.post("/rooms")
def create_room(name: str, db: Session = Depends(get_db)):
    if db.query(Room).filter_by(name=name).first(): raise HTTPException(400, "Exists")
    r = Room(name=name); db.add(r); db.commit(); return {"id": r.id, "name": r.name}

@router.websocket("/ws/{room}")
async def ws_endpoint(websocket: WebSocket, room: str):
    await hub.join(room, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await hub.broadcast(room, data)
    except WebSocketDisconnect:
        await hub.leave(room, websocket)

@router.post("/reports")
def create_report(project_id: int, level: str, details: str = "", db: Session = Depends(get_db)):
    rep = Report(project_id=project_id, level=level, details=details); db.add(rep); db.commit(); return {"id": rep.id}

@router.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    return [{"id": r.id, "project_id": r.project_id, "level": r.level, "details": r.details} for r in db.query(Report).all()]

@router.post("/ratings")
def rate(agent_id: int, capability: str, score: float, db: Session = Depends(get_db)):
    if score < 0 or score > 100: raise HTTPException(400, "0-100 only")
    r = Rating(agent_id=agent_id, capability=capability, score=score, votes=1)
    db.add(r); db.commit(); return {"id": r.id}

@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    data = db.query(Rating).all()
    out = {}
    for r in data:
        out.setdefault((r.agent_id, r.capability), []).append(r.score)
    return [{"agent_id": aid, "capability": cap, "avg": sum(scores)/len(scores)} for (aid, cap), scores in out.items()]
