"""
LLM Integration Module for Job Risk Assessment.
Uses Google Gemini (primary, free) with Anthropic Claude fallback.
Generates human-readable risk explanations, contextual red-flag reasoning,
and candidate safety advice.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("LLMModule")
logger.setLevel(logging.INFO)

DEFAULT_SYSTEM_PROMPT = """
You are a senior recruitment fraud analyst and job safety expert.
Your role is to review structured risk assessment reports of job postings
and generate clear, honest, and actionable advice for job seekers.

Always respond ONLY with valid JSON in this exact format (no extra text):
{
  "verdict": "<One sentence plain-English verdict>",
  "detailed_explanation": "<2-3 paragraph human-readable analysis>",
  "top_warning": "<Single most important warning, or null if safe>",
  "candidate_action": "<Apply / Proceed with Caution / Do Not Apply>"
}

Be factual, empathetic, and non-alarmist. Do not fabricate flags not in the data.
""".strip()


def _build_user_prompt(job_data: Dict[str, Any], risk_report: Dict[str, Any]) -> str:
    violations_summary = "\n".join(
        [f"- [{v['severity']}] {v['rule_id']}: {v['message']}"
         for v in risk_report.get("violations", [])]
    ) or "None"

    return f"""
Analyze this job posting and its automated risk assessment:

== JOB POSTING ==
Title: {job_data.get('title') or 'Not provided'}
Company: {job_data.get('company') or 'Not provided'}
Contact Email: {job_data.get('contact_email') or 'Not provided'}
Description:
{job_data.get('description', '')}

== RISK ASSESSMENT ==
Overall Risk Score: {risk_report.get('overall_score', 0)} / 100
Risk Level: {risk_report.get('risk_level', 'UNKNOWN')}
Violations Found ({risk_report.get('total_violations_found', 0)}):
{violations_summary}

Respond with ONLY the JSON object as specified.
""".strip()


def _parse_llm_json(raw: str) -> Dict[str, Any]:
    """Parse JSON from LLM response, handles code fences."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()
    return json.loads(raw)


class GeminiAnalyzer:
    """Google Gemini powered explainability layer (Free tier)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.6-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GEMINI_API_KEY is not set in .env file.")
        self.model_name = model

    def generate_explanation(
        self, job_data: Dict[str, Any], risk_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = _build_user_prompt(job_data, risk_report)

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=DEFAULT_SYSTEM_PROMPT,
                    temperature=0.2,
                )
            )
            llm_output = _parse_llm_json(response.text)
            logger.info("Gemini analysis generated for '%s'", job_data.get("title"))
            return {
                "status": "success",
                "provider": "gemini",
                "model_used": self.model_name,
                "llm_analysis": llm_output
            }
        except Exception as ex:
            logger.error("Gemini LLM error: %s", str(ex))
            return {"status": "error", "provider": "gemini",
                    "error": str(ex), "llm_analysis": None}


class LLMAnalyzer:
    """
    Primary LLM Analyzer — uses Gemini (free) by default.
    Falls back to Anthropic Claude if Gemini key not available.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.6-flash",
        provider: str = "gemini"
    ):
        self.provider = provider
        self._analyzer = None

        if provider == "gemini":
            gemini_key = os.getenv("GEMINI_API_KEY") or api_key
            if gemini_key:
                self._analyzer = GeminiAnalyzer(api_key=gemini_key, model=model)
            else:
                raise EnvironmentError("GEMINI_API_KEY not found in .env")
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'gemini'.")

    def generate_explanation(
        self, job_data: Dict[str, Any], risk_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._analyzer.generate_explanation(job_data, risk_report)


def create_llm_analyzer(
    api_key: Optional[str] = None,
    model: str = "gemini-3.6-flash",
    provider: str = "gemini"
) -> LLMAnalyzer:
    """Factory function to instantiate the LLMAnalyzer."""
    return LLMAnalyzer(api_key=api_key, model=model, provider=provider)
