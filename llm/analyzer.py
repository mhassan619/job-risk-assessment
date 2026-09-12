"""
LLM Integration Module for Job Risk Assessment.
Uses Anthropic Claude to generate human-readable risk explanations,
contextual red-flag reasoning, and candidate safety advice.
"""

import logging
import os
from typing import Any, Dict, Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("LLMModule")
logger.setLevel(logging.INFO)

DEFAULT_SYSTEM_PROMPT = """
You are a senior recruitment fraud analyst and job safety expert.
Your role is to review structured risk assessment reports of job postings
and generate clear, honest, and actionable advice for job seekers.

Always respond in the following JSON format:
{
  "verdict": "<One sentence plain-English verdict>",
  "detailed_explanation": "<2-3 paragraph human-readable analysis of why this job is or isn't risky>",
  "top_warning": "<Single most important warning for the candidate, or null if safe>",
  "candidate_action": "<What the candidate should do next: Apply / Proceed with Caution / Do Not Apply>"
}

Be factual, empathetic, and non-alarmist. Do not fabricate flags not in the data.
""".strip()


class LLMAnalyzer:
    """
    Anthropic Claude-powered explainability layer.
    Converts raw risk engine output into human-readable, contextual analysis.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022",
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. Add it to your .env file or environment variables."
            )
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens

    def generate_explanation(
        self, job_data: Dict[str, Any], risk_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sends job posting details + risk report to Claude and gets
        a structured, human-readable explanation.
        """
        # Build structured prompt payload
        violations_summary = "\n".join(
            [
                f"- [{v['severity']}] {v['rule_id']}: {v['message']}"
                for v in risk_report.get("violations", [])
            ]
        ) or "None"

        user_message = f"""
Please analyze the following job posting and its automated risk assessment:

== JOB POSTING ==
Title: {job_data.get('title') or 'Not provided'}
Company: {job_data.get('company') or 'Not provided'}
Contact Email: {job_data.get('contact_email') or 'Not provided'}
Description:
{job_data.get('description', '')}

== AUTOMATED RISK ASSESSMENT RESULTS ==
Overall Risk Score: {risk_report.get('overall_score', 0)} / 100
Risk Level: {risk_report.get('risk_level', 'UNKNOWN')}
Violations Found ({risk_report.get('total_violations_found', 0)}):
{violations_summary}

Generate a structured analysis following the JSON format in your system instructions.
""".strip()

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=DEFAULT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )

            raw_content = response.content[0].text.strip()

            # Parse JSON from Claude's response
            import json
            # Handle cases where Claude wraps JSON in code fences
            if raw_content.startswith("```"):
                raw_content = raw_content.strip("`").strip()
                if raw_content.startswith("json"):
                    raw_content = raw_content[4:].strip()

            llm_output = json.loads(raw_content)
            logger.info("LLM analysis generated for '%s'", job_data.get("title"))
            return {
                "status": "success",
                "llm_analysis": llm_output,
                "model_used": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

        except anthropic.AuthenticationError:
            logger.error("Invalid Anthropic API key.")
            return {
                "status": "error",
                "error": "Invalid or expired ANTHROPIC_API_KEY.",
                "llm_analysis": None,
            }
        except anthropic.RateLimitError:
            logger.warning("Anthropic rate limit hit.")
            return {
                "status": "error",
                "error": "API rate limit exceeded. Please retry shortly.",
                "llm_analysis": None,
            }
        except Exception as ex:
            logger.error("LLM generation error: %s", str(ex), exc_info=True)
            return {
                "status": "error",
                "error": f"LLM analysis failed: {str(ex)}",
                "llm_analysis": None,
            }


# Module-level factory
def create_llm_analyzer(
    api_key: Optional[str] = None,
    model: str = "claude-3-5-haiku-20241022"
) -> LLMAnalyzer:
    """Factory function to instantiate the LLMAnalyzer."""
    return LLMAnalyzer(api_key=api_key, model=model)
