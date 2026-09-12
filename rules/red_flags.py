"""
Production-Grade Red-Flag Rule Engine for Job Risk Assessment.
Evaluates job postings against real-world scam patterns, fraud signatures,
and suspicious recruitment practices.
"""

from dataclasses import dataclass, asdict
from enum import Enum
import re
from typing import Any, List, Optional
from urllib.parse import urlparse


class Severity(str, Enum):
    CRITICAL = "CRITICAL"  # Definite scam indicator (e.g. advance fee, money mule)
    HIGH = "HIGH"          # High probability of fraud (e.g. telegram-only, sensitive PII)
    MEDIUM = "MEDIUM"      # Suspicious signal (e.g. free email domain, vague duties)
    LOW = "LOW"            # Cautionary warning (e.g. pressure tactics, buzzwords)


@dataclass
class RuleViolation:
    rule_id: str
    category: str
    severity: Severity
    weight: int
    matched_snippet: str
    message: str
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["severity"] = self.severity.value
        return result


# -------------------------------------------------------------------------
# Detection Signatures & Dictionaries
# -------------------------------------------------------------------------

# 1. Advance-Fee & Financial Fraud Patterns
FINANCIAL_FRAUD_PATTERNS = [
    (r"\b(?:registration|application|processing|background check|screening|equipment|starter kit)\s+fee\b",
     "Advance payment / processing fee required"),
    (r"\b(?:buy|purchase)\s+(?:your own\s+)?(?:equipment|materials|software|laptop)\s+(?:from our|via our|through our)?\s*(?:vendor|supplier|portal)?\b",
     "Candidate required to buy equipment from specified vendor"),
    (r"\b(?:send|wire|deposit|transfer)\s+(?:money|funds|cash|crypto|bitcoin|usdt)\b",
     "Direct monetary or cryptocurrency transfer requested"),
    (r"\b(?:gift card|itunes card|amazon gift|prepaid card|cashapp|zelle|venmo)\b",
     "Irreversible payment method (gift card / cash app) mentioned"),
    (r"\b(?:fake check|cashier check|mobile deposit|reimbursement check)\b",
     "Check deposit / reimbursement scheme detected"),
    (r"\b(?:upfront|advance)\s+(?:payment|deposit|cost|charge)\b",
     "Upfront payment or deposit demanded"),
]

# 2. Money Mule & Illegal Reshipping Patterns
MONEY_MULE_PATTERNS = [
    (r"\b(?:package forwarding|re-shipping|reshipping agent|package inspector)\b",
     "Reshipping or stolen package forwarding scam indicator"),
    (r"\b(?:payment processing assistant|fund transfer agent|financial manager at home)\b",
     "Money mule / illicit fund routing position"),
    (r"\b(?:receive packages?|store goods?|ship items?)\s+(?:at|from)\s+home\b",
     "At-home receiving and reshipping of goods"),
    (r"\b(?:receive funds?|receive payment|transfer into your personal account)\b",
     "Requesting use of candidate's personal bank account for company transactions"),
]

# 3. Off-Platform / Unofficial Communication Channels
OFF_PLATFORM_PATTERNS = [
    (r"\b(?:contact|dm|message|reach)\s+(?:us\s+)?(?:on|via)?\s*(?:telegram|signal|whatsapp|skype|viber)\b",
     "Recruiter asks candidate to move immediately to encrypted/untraceable chat"),
    (r"\btelegram\s*:\s*@?[a-zA-Z0-9_]{4,}\b",
     "Telegram username provided for recruitment"),
    (r"\b(?:t\.me|wa\.me)/[a-zA-Z0-9_]+\b",
     "Direct messaging link to Telegram or WhatsApp"),
    (r"\b(?:interview|chat)\s+(?:via|on)\s+(?:hangouts|google chat|telegram)\b",
     "Informal text-only interview channel specified"),
]

# 4. Sensitive PII / Identity Theft Before Offer
SENSITIVE_PII_PATTERNS = [
    (r"\b(?:ssn|social security number|national identity|cnic|passport copy|driver'?s license)\s*(?:required|needed|to apply|before interview)\b",
     "Critical personal identification requested prior to legitimate offer"),
    (r"\b(?:bank account details|routing number|credit score report)\s*(?:before|prior to|for application)\b",
     "Banking or credit info requested in job posting"),
]

# 5. Unrealistic Hiring Process / Too Good To Be True
UNREALISTIC_HIRING_PATTERNS = [
    (r"\b(?:no experience|zero experience)\s+(?:needed|required).{0,50}(?:\$|\b)\b(?:[5-9]\d|\d{3,})\s*(?:per hour|/hr|weekly|/week)\b",
     "Exorbitant pay rate offered for completely unskilled / zero-experience role"),
    (r"\b(?:immediate|instant)\s+(?:hiring|job offer|appointment)\s+(?:without|no)\s+(?:interview|test)\b",
     "Immediate job offer guaranteed without standard vetting/interview"),
    (r"\b(?:earn|make)\s+\$\d{3,}\s+(?:daily|a day|per day)\s+(?:working\s+)?(?:1|2|few)\s+hours?\b",
     "Get-rich-quick hourly/daily earning claim"),
]

# 6. Pressure & Urgency Tactics
PRESSURE_TACTICS = [
    (r"\b(?:limited slots|only\s+\d+\s+openings left|act fast|urgent hiring today|hire immediately today)\b",
     "High-pressure artificial urgency designed to bypass critical thinking"),
]

# Free / Public Consumer Email Domains
FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "proton.me", "protonmail.com", "icloud.com",
    "mail.com", "zoho.com", "yandex.com", "gmx.com"
}


# -------------------------------------------------------------------------
# Modular Rule Evaluators
# -------------------------------------------------------------------------

def evaluate_financial_fraud(text: str) -> List[RuleViolation]:
    """Flag advance fee, crypto, check, and equipment purchasing demands."""
    violations = []
    text_lower = text.lower()
    for pattern, desc in FINANCIAL_FRAUD_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            violations.append(
                RuleViolation(
                    rule_id="RULE_FINANCIAL_ADVANCE_FEE",
                    category="Financial Fraud",
                    severity=Severity.CRITICAL,
                    weight=40,
                    matched_snippet=match.group(0),
                    message=desc,
                    recommendation="Legitimate employers never ask candidates for money, equipment fees, or check deposits."
                )
            )
            break
    return violations


def evaluate_money_mule(text: str) -> List[RuleViolation]:
    """Flag reshipping and money laundering operation signatures."""
    violations = []
    text_lower = text.lower()
    for pattern, desc in MONEY_MULE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            violations.append(
                RuleViolation(
                    rule_id="RULE_MONEY_MULE_RESHIPPING",
                    category="Illegal Activity / Mule",
                    severity=Severity.CRITICAL,
                    weight=45,
                    matched_snippet=match.group(0),
                    message=desc,
                    recommendation="Do not accept packages or route funds through personal accounts; this is illegal reshipping."
                )
            )
            break
    return violations


def evaluate_communication_channels(text: str, contact_email: Optional[str] = None, company: Optional[str] = None) -> List[RuleViolation]:
    """Flag off-platform messaging and illegitimate contact emails."""
    violations = []
    text_lower = text.lower()

    # 1. Off-platform apps (Telegram, WhatsApp)
    for pattern, desc in OFF_PLATFORM_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            violations.append(
                RuleViolation(
                    rule_id="RULE_SUSPICIOUS_COMMUNICATION_APP",
                    category="Communication Channels",
                    severity=Severity.HIGH,
                    weight=25,
                    matched_snippet=match.group(0),
                    message=desc,
                    recommendation="Professional recruiters rarely conduct initial interviews exclusively over anonymous chat apps."
                )
            )
            break

    # 2. Free public domain email for a corporate posting
    if contact_email and "@" in contact_email:
        domain = contact_email.split("@")[-1].strip().lower()
        if domain in FREE_EMAIL_PROVIDERS:
            # If company name is provided and appears to be an enterprise
            comp_display = f" for '{company}'" if company else ""
            violations.append(
                RuleViolation(
                    rule_id="RULE_FREE_PUBLIC_EMAIL_DOMAIN",
                    category="Identity & Verification",
                    severity=Severity.MEDIUM,
                    weight=20,
                    matched_snippet=contact_email,
                    message=f"Recruiter email uses a generic public provider (@{domain}){comp_display}",
                    recommendation="Verify the recruiter's official company domain email on LinkedIn or the corporate careers page."
                )
            )

    return violations


def evaluate_sensitive_pii(text: str) -> List[RuleViolation]:
    """Flag premature requests for SSN, National ID, or bank details."""
    violations = []
    text_lower = text.lower()
    for pattern, desc in SENSITIVE_PII_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            violations.append(
                RuleViolation(
                    rule_id="RULE_PREMATURE_PII_HARVESTING",
                    category="Identity Theft",
                    severity=Severity.HIGH,
                    weight=30,
                    matched_snippet=match.group(0),
                    message=desc,
                    recommendation="Never provide identity numbers, bank accounts, or IDs prior to an official job offer."
                )
            )
            break
    return violations


def evaluate_unrealistic_terms(text: str) -> List[RuleViolation]:
    """Flag unrealistic compensation claims and instant hiring promises."""
    violations = []
    text_lower = text.lower()
    for pattern, desc in UNREALISTIC_HIRING_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            violations.append(
                RuleViolation(
                    rule_id="RULE_TOO_GOOD_TO_BE_TRUE",
                    category="Compensation & Process",
                    severity=Severity.HIGH,
                    weight=25,
                    matched_snippet=match.group(0),
                    message=desc,
                    recommendation="High pay for low-skill remote work with zero vetting is a classic hook for employment scams."
                )
            )
            break
    return violations


def evaluate_job_content_quality(description: str) -> List[RuleViolation]:
    """Check text length, vague job duties, or missing content."""
    violations = []
    words = description.split()
    word_count = len(words)

    if word_count < 30:
        violations.append(
            RuleViolation(
                rule_id="RULE_VAGUE_JOB_DESCRIPTION",
                category="Content Quality",
                severity=Severity.MEDIUM,
                weight=15,
                matched_snippet=f"Length: {word_count} words",
                message="Extremely brief or vague job description lacking responsibilities and requirements",
                recommendation="Legitimate job posts contain detailed job duties, required qualifications, and company background."
            )
        )

    # Pressure tactics
    for pattern, desc in PRESSURE_TACTICS:
        match = re.search(pattern, description.lower())
        if match:
            violations.append(
                RuleViolation(
                    rule_id="RULE_HIGH_PRESSURE_URGENCY",
                    category="Recruitment Ethics",
                    severity=Severity.LOW,
                    weight=10,
                    matched_snippet=match.group(0),
                    message=desc,
                    recommendation="Scammers create artificial urgency to force quick decisions without proper vetting."
                )
            )
            break

    return violations


# -------------------------------------------------------------------------
# Master Orchestration Function
# -------------------------------------------------------------------------

def run_all_red_flags(job_data: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluates a full job post dictionary against all red flag rules.

    Input schema:
    {
        "title": str,
        "company": str,
        "description": str,
        "contact_email": Optional[str],
        "salary_text": Optional[str],
        "location": Optional[str]
    }

    Returns:
    {
        "total_violations": int,
        "critical_count": int,
        "high_count": int,
        "medium_count": int,
        "low_count": int,
        "total_rule_weight": int,
        "violations": list[dict]
    }
    """
    title = str(job_data.get("title") or "")
    company = str(job_data.get("company") or "")
    description = str(job_data.get("description") or "")
    contact_email = str(job_data.get("contact_email") or "")
    salary_text = str(job_data.get("salary_text") or "")

    # Combine text fields for holistic textual scanning
    full_text = f"{title}\n{salary_text}\n{description}"

    violations: List[RuleViolation] = []
    violations.extend(evaluate_financial_fraud(full_text))
    violations.extend(evaluate_money_mule(full_text))
    violations.extend(evaluate_communication_channels(full_text, contact_email, company))
    violations.extend(evaluate_sensitive_pii(full_text))
    violations.extend(evaluate_unrealistic_terms(full_text))
    violations.extend(evaluate_job_content_quality(description))

    # Calculate severity aggregates
    critical = sum(1 for v in violations if v.severity == Severity.CRITICAL)
    high = sum(1 for v in violations if v.severity == Severity.HIGH)
    medium = sum(1 for v in violations if v.severity == Severity.MEDIUM)
    low = sum(1 for v in violations if v.severity == Severity.LOW)
    total_weight = sum(v.weight for v in violations)

    return {
        "total_violations": len(violations),
        "critical_count": critical,
        "high_count": high,
        "medium_count": medium,
        "low_count": low,
        "total_rule_weight": total_weight,
        "violations": [v.to_dict() for v in violations]
    }
