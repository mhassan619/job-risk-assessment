def validate_input(job_text: str, email: str = None, url: str = None) -> dict:
    """Validates input before it enters the pipeline. Returns errors if any."""
    errors = []

    if not job_text or not job_text.strip():
        errors.append("Job posting text is required and cannot be empty.")
    elif len(job_text.strip()) < 20:
        errors.append("Job posting text is too short to analyze meaningfully.")
    elif len(job_text.strip()) > 8000:
        errors.append("Job posting text is too long (max 8000 characters).")

    if email and "@" not in email:
        errors.append("Email format looks invalid.")

    return {"valid": len(errors) == 0, "errors": errors}