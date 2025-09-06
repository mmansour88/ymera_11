
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")

def add_usage(db: Session, org_id: int, usd: Decimal, tokens_in: int, tokens_out: int):
    # ensure table exists (migration 0005 creates it)
    db.execute(
        "INSERT INTO usage_counters(org_id, month, usd, tokens_in, tokens_out) VALUES (:o,:m,:u,:ti,:to)",
        {"o": org_id, "m": month_key(datetime.utcnow()), "u": float(usd), "ti": tokens_in, "to": tokens_out}
    )
    db.commit()

def current_usage(db: Session, org_id: int) -> float:
    row = db.execute("SELECT COALESCE(SUM(usd),0) FROM usage_counters WHERE org_id=:o AND month=:m",
                     {"o": org_id, "m": month_key(datetime.utcnow())}).fetchone()
    return float(row[0] or 0.0)

def budget_limit(db: Session, org_id: int) -> float:
    row = db.execute("SELECT monthly_usd_limit FROM budgets WHERE org_id=:o", {"o": org_id}).fetchone()
    return float(row[0]) if row else 0.0

def enforce_budget(db: Session, org_id: int):
    limit = budget_limit(db, org_id)
    if limit <= 0:
        return  # disabled
    used = current_usage(db, org_id)
    if used >= limit:
        raise RuntimeError(f"Budget exceeded for org {org_id}: used ${used:.2f} / limit ${limit:.2f}")
