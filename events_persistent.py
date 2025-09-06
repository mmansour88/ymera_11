import os, hmac, hashlib, json, asyncio, httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models.webhooks import WebhookSubscriber, WebhookDelivery

MAX_RETRY = int(os.getenv("WEBHOOK_RETRY_MAX","5") or 5)
BASE_DELAY = float(os.getenv("WEBHOOK_RETRY_BASE","2.0") or 2.0)

async def _deliver(sub: WebhookSubscriber, delivery: WebhookDelivery):
    payload = json.dumps(delivery.payload)
    headers = {"Content-Type": "application/json"}
    if sub.secret:
        sig = hmac.new(sub.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        headers["X-YMERA-Signature"] = sig
    async with httpx.AsyncClient(timeout=10) as cx:
        r = await cx.post(sub.url, headers=headers, content=payload)
        return r

async def worker():
    while True:
        try:
            db: Session = SessionLocal()
            now = datetime.utcnow()
            q = db.query(WebhookDelivery).filter(WebhookDelivery.status=="pending", WebhookDelivery.next_attempt_at<=now).order_by(WebhookDelivery.id.asc()).limit(20)
            items = q.all()
            for d in items:
                sub = db.query(WebhookSubscriber).get(d.subscriber_id)
                if not sub or not sub.active:
                    d.status = "failed"; d.last_error = "inactive subscriber"; db.commit(); continue
                try:
                    r = await _deliver(sub, d)
                    if r.status_code < 300:
                        d.status = "success"; d.delivered_at = datetime.utcnow()
                    else:
                        d.attempts += 1
                        d.last_error = f"HTTP {r.status_code}"
                        if d.attempts >= MAX_RETRY:
                            d.status = "failed"
                        else:
                            d.next_attempt_at = datetime.utcnow() + timedelta(seconds=(BASE_DELAY * (2 ** (d.attempts-1))))
                    db.commit()
                except Exception as e:
                    d.attempts += 1
                    d.last_error = str(e)[:300]
                    if d.attempts >= MAX_RETRY:
                        d.status = "failed"
                    else:
                        d.next_attempt_at = datetime.utcnow() + timedelta(seconds=(BASE_DELAY * (2 ** (d.attempts-1))))
                    db.commit()
            db.close()
        except Exception:
            pass
        await asyncio.sleep(1)

def enqueue(topic: str, payload: dict):
    db: Session = SessionLocal()
    subs = db.query(WebhookSubscriber).filter(WebhookSubscriber.topic==topic, WebhookSubscriber.active==True).all()
    for s in subs:
        d = WebhookDelivery(subscriber_id=s.id, topic=topic, payload=payload, status="pending")
        db.add(d)
    db.commit()
    db.close()
