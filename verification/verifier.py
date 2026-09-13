from verification.email_check import check_email
from verification.url_check import check_url
from verification.company_check import check_company_mention

def run_verification(job_text: str, email: str = None, url: str = None) -> dict:
    email_result = check_email(email)
    url_result = check_url(url)
    company_result = check_company_mention(job_text)

    flags = []
    if email_result.get("flag"):
        flags.append(email_result["flag"])
    if url_result.get("flags"):
        flags.extend(url_result["flags"])
    if company_result.get("flag"):
        flags.append(company_result["flag"])

    total_weight = sum(f["weight"] for f in flags)

    return {
        "email_check": email_result,
        "url_check": url_result,
        "company_check": company_result,
        "verification_flags": flags,
        "total_verification_weight": total_weight
    }