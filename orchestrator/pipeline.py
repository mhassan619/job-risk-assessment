from orchestrator.validator import validate_input
from orchestrator.safe_runner import safe_run

from rules.rule_engine import run_all_rules
from llm.analyzer import analyze_with_llm
from verification.verifier import run_verification
from risk_engine.scorer import calculate_risk
from llm.explanation import generate_explanation

RULE_FALLBACK = {"triggered_rules": [], "rule_count": 0, "total_rule_weight": 0}
LLM_FALLBACK = {"contextual_flags": [], "overall_impression": "Analysis unavailable.", "llm_certainty": "low"}
VERIFICATION_FALLBACK = {"email_check": {}, "url_check": {}, "company_check": {}, "verification_flags": [], "total_verification_weight": 0}


def run_pipeline(job_text: str, email: str = None, url: str = None) -> dict:
    validation = validate_input(job_text, email, url)
    if not validation["valid"]:
        return {"success": False, "errors": validation["errors"]}

    rule_result = safe_run("RuleEngine", run_all_rules, job_text, email=email, fallback=RULE_FALLBACK)
    llm_result = safe_run("LLMAnalyzer", analyze_with_llm, job_text, email, url, fallback=LLM_FALLBACK)
    verification_result = safe_run("Verifier", run_verification, job_text, email, url, fallback=VERIFICATION_FALLBACK)

    risk = calculate_risk(rule_result, llm_result, verification_result)

    explanation = safe_run(
        "ExplanationGenerator", generate_explanation,
        job_text, rule_result, llm_result, verification_result, risk,
        fallback={"explanation": "Unable to generate a detailed explanation at this time.",
                  "recommendation": "Please manually review this posting carefully before proceeding."}
    )

    return {
        "success": True,
        "risk_score": risk["final_score"],
        "risk_level": risk["risk_level"],
        "confidence": risk["confidence"],
        "breakdown": risk["breakdown"],
        "rule_flags": rule_result.get("triggered_rules", []),
        "llm_flags": llm_result.get("contextual_flags", []),
        "verification_flags": verification_result.get("verification_flags", []),
        "explanation": explanation.get("explanation"),
        "recommendation": explanation.get("recommendation"),
        "degraded": any([
            rule_result.get("_component_failed"),
            llm_result.get("_component_failed"),
            verification_result.get("_component_failed")
        ])
    }