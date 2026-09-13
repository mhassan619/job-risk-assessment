SEVERITY_WEIGHTS = {
    "low": 3,
    "medium": 6,
    "high": 9
}

def get_llm_weights(analysis_result: dict) -> list:
    flags = analysis_result.get("contextual_flags", [])
    return [SEVERITY_WEIGHTS.get(f.get("severity", "low"), 3) for f in flags]


def calculate_llm_weight(analysis_result: dict) -> int:
    return sum(get_llm_weights(analysis_result))