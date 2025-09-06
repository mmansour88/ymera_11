
import os, time, hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis

def _redis():
    url = os.getenv("REDIS_URL","redis://redis:6379/0")
    return redis.Redis.from_url(url, decode_responses=True)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rpm_default = int(os.getenv("RATE_LIMIT_RPM_DEFAULT","60"))
        self.window = 60
        self.r = _redis()

    async def dispatch(self, request, call_next):
        auth = request.headers.get("authorization","")
        sub = "anon"
        if auth.startswith("Bearer "):
            sub = hashlib.sha1(auth.encode()).hexdigest()[:10]
        org = request.headers.get("x-org-id","0")
        path = request.url.path.split("?")[0]
        key = f"rl:{org}:{sub}:{path}:{int(time.time()//self.window)}"
        used = self.r.incr(key, 1)
        if used == 1:
            self.r.expire(key, self.window+5)
        if used > self.rpm_default:
            retry = self.r.ttl(key)
            return JSONResponse({"error":"rate_limited","retry_after":retry}, status_code=429)
        return await call_next(request)
