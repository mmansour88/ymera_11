
from datetime import datetime
import math, httpx

async def tool_now(params):
    return {"now": datetime.utcnow().isoformat() + "Z"}

async def tool_math(params):
    # VERY SAFE sandboxed eval for +,-,*,/,**, (), numbers only
    expr = str(params.get("expr","")).strip()
    if not expr.replace("+","").replace("-","").replace("*","").replace("/","").replace("(","").replace(")","").replace(".","").replace("**","").replace(" ","").isdigit():
        # fallback: disallow anything else
        raise ValueError("Unsafe expression")
    try:
        val = eval(expr, {"__builtins__":{}}, {"math": math})
    except Exception as e:
        return {"error": str(e)}
    return {"result": val}

async def tool_http_get(params):
    url = params.get("url")
    if not (str(url).startswith("https://") or str(url).startswith("http://")):
        return {"error":"Only http/https allowed"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url)
        return {"status": r.status_code, "text": r.text[:5000]}

TOOLS = {
    "now": tool_now,
    "math": tool_math,
    "http_get": tool_http_get,
}
