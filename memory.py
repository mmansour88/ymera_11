
import os, math, json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
import httpx

# NOTE: ORM model is managed via Alembic (vector column). We keep JSON as a fallback mirror.

async def embed_text(text: str) -> List[float]:
    oai = os.getenv("OPENAI_API_KEY")
    model = os.getenv("EMBEDDING_MODEL","text-embedding-3-small")
    if oai:
        payload = {"model": model, "input": text}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post("https://api.openai.com/v1/embeddings", json=payload, headers={"Authorization": f"Bearer {oai}"})
            r.raise_for_status()
            j = r.json()
            return j["data"][0]["embedding"]
    import hashlib, random
    h = hashlib.sha256(text.encode()).digest()
    random.seed(h)
    return [random.random() for _ in range(128)]

def _cosine(a: List[float], b: List[float]) -> float:
    num = sum(x*y for x,y in zip(a,b))
    da = math.sqrt(sum(x*x for x in a)) or 1e-9
    db = math.sqrt(sum(x*x for x in b)) or 1e-9
    return num/(da*db)

async def upsert_memory(db: Session, org_id: int, namespace: str, key: str, text: str) -> Dict[str,Any]:
    vec = await embed_text(text)
    # use JSON mirror always; vector column if available via trigger or direct update
    ex = db.execute(
        "SELECT id FROM memory_items WHERE org_id=:org AND namespace=:ns AND key=:k",
        {"org": org_id, "ns": namespace, "k": key}
    ).fetchone()
    if ex:
        db.execute("UPDATE memory_items SET text=:t, vector_json=:v WHERE id=:id", {"t": text, "v": json.dumps(vec), "id": ex[0]})
        db.commit()
        return {"id": ex[0], "updated": True}
    else:
        db.execute("INSERT INTO memory_items(org_id, namespace, key, text, vector_json) VALUES (:o,:n,:k,:t,:v)",
                   {"o":org_id,"n":namespace,"k":key,"t":text,"v":json.dumps(vec)})
        db.commit()
        rid = db.execute("SELECT currval(pg_get_serial_sequence('memory_items','id'))").fetchone()[0]
        return {"id": rid, "created": True}

def search_memory(db: Session, org_id: int, namespace: str, query_vec: List[float], top_k: int=5) -> List[Dict[str,Any]]:
    # Prefer pgvector if column exists; fallback to JSON cosine
    try:
        rows = db.execute(
            """
            SELECT id, key, text, 1 - (vector <=> cube(array[{}])) AS score
            FROM memory_items
            WHERE org_id=:org AND namespace=:ns AND vector IS NOT NULL
            ORDER BY vector <=> cube(array[{}]) ASC
            LIMIT :k
            """.format(",".join(str(x) for x in query_vec), ",".join(str(x) for x in query_vec)),
            {"org": org_id, "ns": namespace, "k": top_k}
        ).fetchall()
        return [{"id": r[0], "key": r[1], "text": r[2], "score": float(r[3])} for r in rows]
    except Exception:
        rows = db.execute(
            "SELECT id, key, text, vector_json FROM memory_items WHERE org_id=:org AND namespace=:ns",
            {"org": org_id, "ns": namespace}
        ).fetchall()
        scored = []
        for r in rows:
            vec = json.loads(r[3] or "[]")
            scored.append({"id": r[0], "key": r[1], "text": r[2], "score": _cosine(query_vec, vec)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
