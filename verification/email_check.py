import re

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "icloud.com", "protonmail.com", "yandex.com"
}

def is_valid_email_format(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip())) if email else False


def check_email(email: str) -> dict:
    """Returns verification findings for the email — never raises, always returns a dict."""
    if not email:
        return {
            "provided": False,
            "valid_format": None,
            "domain_type": None,
            "flag": None
        }

    email = email.strip()

    if not is_valid_email_format(email):
        return {
            "provided": True,
            "valid_format": False,
            "domain_type": None,
            "flag": {"description": "Email format is invalid or malformed", "weight": 4}
        }

    domain = email.split("@")[-1].lower()
    is_free = domain in FREE_EMAIL_DOMAINS

    return {
        "provided": True,
        "valid_format": True,
        "domain": domain,
        "domain_type": "free/generic" if is_free else "custom/company",
        "flag": (
            {"description": f"Recruiter using free email domain ({domain})", "weight": 5}
            if is_free else None
        )
    }