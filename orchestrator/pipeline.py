"""
Orchestrator: Central pipeline coordinator for Job Risk Assessment.
Wires together:  Input → API Handler → Risk Engine → LLM Explanation → Final Report
"""

import logging
from typing import Any, Dict, Optional

from risk_engine.api_handler import JobRiskAPIHandler, APIValidationError
from risk_engine.scoring import RiskScoringEngine
from llm.analyzer import LLMAnalyzer

logger = logging.getLogger("Orchestrator")
logger.setLevel(logging.INFO)


class AssessmentOrchestrator:
    """
    Top-level pipeline coordinator.
    Handles full end-to-end assessment: validation → scoring → LLM enrichment → report.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_llm: bool = True,
        llm_model: str = "gemini-3.6-flash",
    ):
        self.scoring_engine = RiskScoringEngine()
        self.api_handler = JobRiskAPIHandler(scoring_engine=self.scoring_engine)
        self.enable_llm = enable_llm
        self._llm_analyzer: Optional[LLMAnalyzer] = None

        if enable_llm:
            try:
                self._llm_analyzer = LLMAnalyzer(api_key=api_key, model=llm_model)
                logger.info("LLM Analyzer initialized successfully.")
            except EnvironmentError as e:
                logger.warning("LLM disabled: %s", str(e))
                self._llm_analyzer = None
                self.enable_llm = False

    def run(self, job_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full assessment pipeline for a single job posting.

        Input:
            job_payload: dict with keys: title, company, description, contact_email, etc.

        Output:
            Combined report dict with structured risk assessment + optional LLM explanation.
        """
        logger.info("Starting assessment pipeline for: '%s'", job_payload.get("title", "Unknown"))

        # Stage 1: Validate + Score
        api_response = self.api_handler.handle_assessment_request(job_payload)

        if api_response.get("status") != "success":
            # Propagate validation or server error immediately
            return api_response

        assessment_data = api_response["data"]["assessment"]
        job_metadata = api_response["data"]["job_metadata"]
        warnings = api_response["data"].get("warnings", [])

        # Stage 2: LLM Enrichment (if enabled and API key available)
        llm_result: Dict[str, Any] = {}
        if self.enable_llm and self._llm_analyzer:
            llm_result = self._llm_analyzer.generate_explanation(
                job_data=job_payload,
                risk_report=assessment_data
            )
        else:
            llm_result = {
                "status": "skipped",
                "reason": "LLM analysis disabled or API key not configured.",
                "llm_analysis": None
            }

        # Stage 3: Compose final unified report
        final_report = {
            "status": "success",
            "code": 200,
            "job_metadata": job_metadata,
            "risk_assessment": {
                "overall_score": assessment_data["overall_score"],
                "risk_level": assessment_data["risk_level"],
                "confidence_score": assessment_data["confidence_score"],
                "summary": assessment_data["summary"],
                "total_violations": assessment_data["total_violations_found"],
                "category_breakdown": assessment_data["category_breakdown"],
                "violations": assessment_data["violations"],
                "safety_recommendations": assessment_data["safety_recommendations"],
            },
            "llm_explanation": llm_result.get("llm_analysis"),
            "llm_status": llm_result.get("status"),
            "warnings": warnings
        }

        logger.info(
            "Assessment complete for '%s' → Risk: %s | Score: %s",
            job_metadata.get("title"),
            assessment_data["risk_level"],
            assessment_data["overall_score"]
        )
        return final_report

    def run_batch(self, job_payloads: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run the assessment pipeline over multiple job postings.
        Returns aggregated batch result with per-job breakdown.
        """
        results = []
        high_count = medium_count = low_count = 0

        for job in job_payloads:
            result = self.run(job)
            results.append(result)
            if result.get("status") == "success":
                level = result["risk_assessment"]["risk_level"]
                if level == "HIGH":
                    high_count += 1
                elif level == "MEDIUM":
                    medium_count += 1
                else:
                    low_count += 1

        return {
            "status": "success",
            "total_analyzed": len(job_payloads),
            "summary": {
                "high_risk_count": high_count,
                "medium_risk_count": medium_count,
                "low_risk_count": low_count,
            },
            "results": results
        }


# Module-level convenience factory
def create_orchestrator(
    api_key: Optional[str] = None,
    enable_llm: bool = True
) -> AssessmentOrchestrator:
    """Creates and returns a configured AssessmentOrchestrator instance."""
    return AssessmentOrchestrator(api_key=api_key, enable_llm=enable_llm, llm_model="gemini-3.6-flash")
