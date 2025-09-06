from fastapi import APIRouter
import hashlib, time

router = APIRouter()
chain = []

def _hash(prev_hash: str, event: str) -> str:
    return hashlib.sha256((prev_hash + event).encode()).hexdigest()

@router.post("/ledger/append")
def append(event: str):
    prev = chain[-1]["checksum"] if chain else "GENESIS"
    checksum = _hash(prev, event)
    block = {"prev_hash": prev, "event": event, "checksum": checksum, "ts": time.time()}
    chain.append(block)
    return block

@router.get("/ledger/verify")
def verify():
    prev = "GENESIS"
    for b in chain:
        if hashlib.sha256((prev + b["event"]).encode()).hexdigest() != b["checksum"]:
            return {"ok": False}
        prev = b["checksum"]
    return {"ok": True, "length": len(chain)}
