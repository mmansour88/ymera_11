import re
RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_PHONE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
RE_CARD = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

def scrub(text: str) -> str:
    t = RE_EMAIL.sub("[email]", text)
    t = RE_PHONE.sub("[phone]", t)
    t = RE_CARD.sub("[card]", t)
    return t
