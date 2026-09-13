import json
import re
from llm.client import call_llm
from llm.prompts import build_analysis_prompt


def extract_json(raw_text: str) -> dict:
    """LLM sometimes wraps JSON in markdown fences, reasoning text, or extra content — clean it first."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*|\s*```$", "", cleaned, flags=re.MULTILINE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        print("\n[DEBUG] Could not parse. Raw LLM output was:\n" + "=" * 50)
        print(raw_text)
        print("=" * 50 + "\n")

        return {
            "contextual_flags": [],
            "overall_impression": "Could not parse LLM response.",
            "llm_certainty": "low",
            "parse_error": True
        }


def analyze_with_llm(job_text: str, email: str = None, url: str = None) -> dict:
    prompt = build_analysis_prompt(job_text, email, url)
    raw_response = call_llm(prompt, max_tokens=800)
    result = extract_json(raw_response)

    result.setdefault("contextual_flags", [])
    result.setdefault("overall_impression", "")
    result.setdefault("llm_certainty", "low")

    return result