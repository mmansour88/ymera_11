
import os, time
from sqlalchemy.orm import Session
from .models import Budget

COST_HINT = {
    "openai": 0.002,      # very rough per-call default
    "anthropic": 0.003,
    "groq": 0.0005,
    "deepseek": 0.0002,
    "gemini": 0.0003,
}

def _today_key():
    return time.strftime("%Y-%m-%d")

# naive in-DB reset: if spent_today_usd > 0 and date changed, reset externally or via cron
def check_and_increment(db: Session, provider: str, est_cost: float=None):
    provider = provider.lower()
    b = db.query(Budget).filter(Budget.provider==provider).first()
    if not b:
        b = Budget(provider=provider, daily_limit_usd=float(os.getenv("BUDGET_LIMIT_"+provider.upper(), 1.0)))
        db.add(b); db.flush()
    est = est_cost if est_cost is not None else COST_HINT.get(provider, 0.001)
    if (b.spent_today_usd or 0) + est > (b.daily_limit_usd or 1.0):
        return False, b
    b.spent_today_usd = (b.spent_today_usd or 0) + est
    db.add(b)
    return True, b
