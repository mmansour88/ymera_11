
BLOCKLIST = {"kill","bomb","explosive","child abuse"}

def sanitize_prompt(text: str) -> str:
    t = (text or "").strip()
    if not t: return t
    for bad in BLOCKLIST:
        if bad in t.lower():
            raise ValueError("unsafe_content")
    # clamp
    if len(t) > 8000:
        t = t[:8000]
    return t
