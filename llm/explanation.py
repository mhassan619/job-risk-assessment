from llm.client import call_llm
from llm.analyzer import extract_json

EXPLANATION_PROMPT = """You are explaining a job-posting risk assessment to a job seeker in plain, simple language.

Risk Score: {score}/100
Risk Level: {level}
Confidence: {confidence}

Evidence found:
- Rule-based flags: {rule_flags}
- Contextual (AI) flags: {llm_flags}
- Verification flags: {verification_flags}

Write a short, clear explanation (2-4 sentences) of WHY this posting received this risk level,
referencing the actual evidence above. Then give one practical safety recommendation.

Respond with ONLY valid JSON in this format:
{{
  "explanation": "...",
  "recommendation": "..."
}}
"""

def generate_explanation(job_text, rule_result, llm_result, verification_result, risk) -> dict:
    rule_summaries = [r["description"] for r in rule_result.get("triggered_rules", [])]
    llm_summaries = [f["flag"] for f in llm_result.get("contextual_flags", [])]
    verification_summaries = [f["description"] for f in verification_result.get("verification_flags", [])]

    prompt = EXPLANATION_PROMPT.format(
        score=risk["final_score"],
        level=risk["risk_level"],
        confidence=risk["confidence"],
        rule_flags=rule_summaries or "none",
        llm_flags=llm_summaries or "none",
        verification_flags=verification_summaries or "none"
    )

    raw = call_llm(prompt, max_tokens=300)
    result = extract_json(raw)

    result.setdefault("explanation", "This posting was evaluated based on the evidence found above.")
    result.setdefault("recommendation", "Verify the company independently before proceeding.")

    return result