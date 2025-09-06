
from sqlalchemy.orm import Session
from .models import UserProviderQuota

def check_and_inc_user_provider_quota(db: Session, user_id: int, provider: str, want:int=1):
    row = db.query(UserProviderQuota).filter(UserProviderQuota.user_id==user_id,
                                            UserProviderQuota.provider==provider.lower()).first()
    if not row:
        row = UserProviderQuota(user_id=user_id, provider=provider.lower(), daily_calls=50, used_today=0)
        db.add(row); db.flush()
    if (row.used_today or 0) + want > (row.daily_calls or 0):
        return False
    row.used_today = (row.used_today or 0) + want
    db.add(row)
    return True
