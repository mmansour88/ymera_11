
import time
from sqlalchemy.orm import Session
from .models import UserQuota

def check_and_inc_user_quota(db: Session, user_id: int, want: int=1):
    uq = db.query(UserQuota).filter(UserQuota.user_id==user_id).first()
    if not uq:
        uq = UserQuota(user_id=user_id, daily_calls=100, used_today=0)
        db.add(uq); db.flush()
    # naive daily reset is expected via external job
    if (uq.used_today or 0) + want > (uq.daily_calls or 0):
        return False
    uq.used_today = (uq.used_today or 0) + want
    db.add(uq)
    return True
