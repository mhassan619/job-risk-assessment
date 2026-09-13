from risk_engine.config import MAX_TOTAL_WEIGHT, RISK_BANDS, HARD_CRITICAL_CATEGORIES, HARD_CRITICAL_FLOOR
from risk_engine.normalizer import normalize
from llm.severity_map import get_llm_weights

DIMINISH_FACTOR = 0.5


def diminishing_sum(weights: list) -> float:
    if not weights:
        return 0.0
    sorted_weights = sorted(weights, reverse=True)
    return sum(w * (DIMINISH_FACTOR ** i) for i, w in enumerate(sorted_weights))


def get_risk_level(score: float) -> str:
    for low, high, label in RISK_BANDS:
        if low <= score <= high:
            return label
    return "Unknown"


def calculate_confidence(rule_count, llm_flag_count, verification_flag_count, llm_certainty):
    total_signals = rule_count + llm_flag_count + verification_flag_count
    certainty_score = {"high": 2, "medium": 1, "low": 0}.get(llm_certainty, 0)
    combined = total_signals + certainty_score

    if combined >= 5:
        return "High"
    elif combined >= 2:
        return "Medium"
    else:
        return "Low"


def calculate_risk(rule_result: dict, llm_result: dict, verification_result: dict) -> dict:
    rule_weights = [r["weight"] for r in rule_result.get("triggered_rules", [])]
    llm_weights = get_llm_weights(llm_result)
    veri_weights = [f["weight"] for f in verification_result.get("verification_flags", [])]

    rule_score = diminishing_sum(rule_weights)
    llm_score = diminishing_sum(llm_weights)
    veri_score = diminishing_sum(veri_weights)

    total_raw = rule_score + llm_score + veri_score
    final_score = round(normalize(total_raw, MAX_TOTAL_WEIGHT), 1)

    triggered_categories = {r["category"] for r in rule_result.get("triggered_rules", [])}
    if triggered_categories & HARD_CRITICAL_CATEGORIES:
        final_score = max(final_score, HARD_CRITICAL_FLOOR)

    risk_level = get_risk_level(final_score)

    confidence = calculate_confidence(
        rule_count=rule_result.get("rule_count", 0),
        llm_flag_count=len(llm_result.get("contextual_flags", [])),
        verification_flag_count=len(verification_result.get("verification_flags", [])),
        llm_certainty=llm_result.get("llm_certainty", "low")
    )

    return {
        "final_score": final_score,
        "risk_level": risk_level,
        "confidence": confidence,
        "breakdown": {
            "rule_diminished": round(rule_score, 1),
            "llm_diminished": round(llm_score, 1),
            "verification_diminished": round(veri_score, 1),
            "total_diminished": round(total_raw, 1)
        }
    }