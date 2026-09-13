def check_company_mention(job_text: str) -> dict:
    """Very lightweight heuristic — checks if a specific company name context exists."""
    text_lower = job_text.lower()

    vague_phrases = [
        "our company", "a leading company", "a reputed organization",
        "our organization", "a growing company"
    ]

    vague_hits = [p for p in vague_phrases if p in text_lower]

    if vague_hits:
        return {
            "flag": {
                "description": "Job posting refers to the company vaguely without naming it",
                "weight": 4
            },
            "matched_phrases": vague_hits
        }

    return {"flag": None, "matched_phrases": []}