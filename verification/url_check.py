import re
from urllib.parse import urlparse

SUSPICIOUS_TLD = {".xyz", ".top", ".click", ".loan", ".work", ".biz"}
URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd"}

def check_url(url: str) -> dict:
    """Pattern-based URL checks only — no live network calls, so this never times out."""
    if not url:
        return {"provided": False, "flags": []}

    flags = []
    try:
        parsed = urlparse(url if "://" in url else f"http://{url}")
        domain = parsed.netloc.lower()
    except Exception:
        return {
            "provided": True,
            "flags": [{"description": "URL could not be parsed — malformed", "weight": 4}]
        }

    if not domain:
        return {
            "provided": True,
            "flags": [{"description": "URL has no valid domain", "weight": 4}]
        }

    if any(domain.endswith(tld) for tld in SUSPICIOUS_TLD):
        flags.append({"description": f"Domain uses a suspicious TLD ({domain})", "weight": 6})

    if any(short in domain for short in URL_SHORTENERS):
        flags.append({"description": "URL uses a link shortener, hiding the real destination", "weight": 7})

    if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        flags.append({"description": "URL uses a raw IP address instead of a domain name", "weight": 8})

    if len(domain) > 40:
        flags.append({"description": "Unusually long/complex domain name", "weight": 3})

    return {"provided": True, "domain": domain, "flags": flags}