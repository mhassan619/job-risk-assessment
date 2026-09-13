import re
from rules.rule_definitions import RULES

CURRENCY_PATTERN = re.compile(r"(\$|Rs\.?|PKR)\s?\d[\d,]*")
FEE_CONTEXT_WORDS = ["fee", "deposit", "purchase", "kit", "uniform", "membership",
                      "activation", "unlock", "processing", "registration",
                      "administrative", "refundable", "training", "equipment",
                      "portfolio", "certificate", "starter"]


def check_keyword_rules(text: str) -> list:
    text_lower = text.lower()
    triggered = []

    for rule in RULES:
        keywords = rule.get("keywords", [])
        if not keywords:
            continue
        for kw in keywords:
            if kw.lower() in text_lower:
                triggered.append({
                    "id": rule["id"],
                    "category": rule["category"],
                    "weight": rule["weight"],
                    "description": rule["description"],
                    "matched_on": kw
                })
                break
    return triggered


def check_email_domain(email: str) -> list:
    if not email or "@" not in email:
        return []

    domain = email.split("@")[-1].lower().strip()
    generic_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]

    if domain in generic_domains:
        return [{
            "id": "R004",
            "category": "contact",
            "weight": 5,
            "description": "Recruiter using free/generic email instead of company domain",
            "matched_on": domain
        }]
    return []


def check_generic_payment_pattern(text: str, already_flagged_payment: bool) -> list:
    """
    Catches upfront-payment scam language that R001/R002's fixed phrase list misses,
    by looking for a monetary amount appearing in the same sentence as fee/deposit/
    purchase-type words (e.g. "purchase our starter kit for $199", "portfolio fee of $85").
    Skipped if a payment rule already fired on this text, to avoid double-counting
    the same evidence twice.
    """
    if already_flagged_payment:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        if CURRENCY_PATTERN.search(sentence):
            lower = sentence.lower()
            if any(w in lower for w in FEE_CONTEXT_WORDS):
                return [{
                    "id": "R012",
                    "category": "payment",
                    "weight": 9,
                    "description": "Mentions a monetary amount alongside fee/deposit/purchase-type language, suggesting payment is requested from the applicant",
                    "matched_on": sentence.strip()[:80]
                }]
    return []


def run_all_rules(job_text: str, email: str = None) -> dict:
    triggered = check_keyword_rules(job_text)
    triggered += check_email_domain(email)

    already_payment = any(r["category"] == "payment" for r in triggered)
    triggered += check_generic_payment_pattern(job_text, already_payment)

    total_weight = sum(r["weight"] for r in triggered)

    return {
        "triggered_rules": triggered,
        "rule_count": len(triggered),
        "total_rule_weight": total_weight
    }