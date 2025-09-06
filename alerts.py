
import os, httpx

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_KEY    = os.getenv("MAILGUN_KEY")
ALERT_TO       = os.getenv("ALERT_TO")

async def send_alert(subject: str, text: str):
    if not (MAILGUN_DOMAIN and MAILGUN_KEY and ALERT_TO):
        return
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_KEY)
    data = {"from": f"YMERA Alerts <alerts@{MAILGUN_DOMAIN}>",
            "to": [ALERT_TO],
            "subject": subject,
            "text": text[:10000]}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(url, auth=auth, data=data)
    except Exception:
        pass
