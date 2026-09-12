"""
Production-Grade API Handler and Backend Service Layer for Job Risk Assessment.
Handles input validation, error handling, payload sanitization, batch processing,
and standardized JSON API response formatting.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
from risk_engine.scoring import RiskScoringEngine, RiskReport, calculate_job_risk

# Setup logger for backend audit trail
logger = logging.getLogger("RiskEngineBackend")
logger.setLevel(logging.INFO)


class APIValidationError(Exception):
    """Raised when input payload fails validation checks."""
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or []


class JobRiskAPIHandler:
    """
    Backend service handling data validation, sanitization,
    scoring orchestration, and standardized API envelope creation.
    """

    def __init__(self, scoring_engine: Optional[RiskScoringEngine] = None):
        self.scoring_engine = scoring_engine or RiskScoringEngine()

    def validate_and_sanitize_input(self, raw_data: Any) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validates structure and data types of the incoming request payload.
        Returns sanitized job dictionary and a list of non-fatal warnings.
        """
        warnings: List[str] = []

        if not isinstance(raw_data, dict):
            raise APIValidationError("Request payload must be a JSON object / dictionary.")

        # Required field: description or content
        description = raw_data.get("description") or raw_data.get("job_description") or raw_data.get("text")
        if not description or not str(description).strip():
            raise APIValidationError("Missing required field: 'description' (or 'job_description') cannot be empty.")

        description = str(description).strip()
        if len(description) < 15:
            warnings.append("Job description is suspiciously brief (<15 characters).")

        # Sanitize optional string fields
        title = str(raw_data.get("title") or "").strip()
        if not title:
            warnings.append("Job 'title' was not provided; analysis will be limited.")

        company = str(raw_data.get("company") or raw_data.get("company_name") or "").strip()
        contact_email = str(raw_data.get("contact_email") or raw_data.get("email") or "").strip()
        salary_text = str(raw_data.get("salary_text") or raw_data.get("salary") or "").strip()
        location = str(raw_data.get("location") or "").strip()
        job_url = str(raw_data.get("job_url") or raw_data.get("url") or "").strip()

        sanitized_job = {
            "title": title,
            "company": company,
            "description": description,
            "contact_email": contact_email,
            "salary_text": salary_text,
            "location": location,
            "job_url": job_url
        }

        return sanitized_job, warnings

    def handle_assessment_request(self, payload: Any) -> Dict[str, Any]:
        """
        Single job analysis endpoint handler.
        Returns a standardized REST-compliant JSON response envelope.
        """
        request_time = datetime.now(timezone.utc).isoformat()

        try:
            # 1. Validation & sanitization
            sanitized_job, warnings = self.validate_and_sanitize_input(payload)

            # 2. Run risk assessment
            report: RiskReport = self.scoring_engine.evaluate_risk(sanitized_job)

            # 3. Build success envelope
            response = {
                "status": "success",
                "code": 200,
                "timestamp": request_time,
                "data": {
                    "job_metadata": {
                        "title": sanitized_job["title"] or "Untitled Posting",
                        "company": sanitized_job["company"] or "Unspecified",
                        "location": sanitized_job["location"] or "Unspecified"
                    },
                    "assessment": report.to_dict(),
                    "warnings": warnings
                }
            }
            logger.info("Successfully analyzed job '%s' - Risk: %s (Score: %s)",
                        sanitized_job["title"], report.risk_level.value, report.overall_score)
            return response

        except APIValidationError as ve:
            logger.warning("Validation failed for assessment request: %s", str(ve))
            return {
                "status": "error",
                "code": 400,
                "timestamp": request_time,
                "error": {
                    "type": "ValidationError",
                    "message": str(ve),
                    "details": ve.errors
                }
            }
        except Exception as ex:
            logger.error("Unexpected error during assessment: %s", str(ex), exc_info=True)
            return {
                "status": "error",
                "code": 500,
                "timestamp": request_time,
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred while processing the risk assessment."
                }
            }

    def handle_batch_assessment_request(self, batch_payload: Any) -> Dict[str, Any]:
        """
        Batch job analysis endpoint handler for multiple job postings.
        """
        request_time = datetime.now(timezone.utc).isoformat()

        if not isinstance(batch_payload, (list, tuple)):
            if isinstance(batch_payload, dict) and "jobs" in batch_payload:
                items = batch_payload["jobs"]
            else:
                return {
                    "status": "error",
                    "code": 400,
                    "timestamp": request_time,
                    "error": {
                        "type": "ValidationError",
                        "message": "Batch payload must be a list of job postings or contain a 'jobs' array."
                    }
                }
        else:
            items = batch_payload

        results = []
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        for idx, item in enumerate(items):
            res = self.handle_assessment_request(item)
            results.append(res)
            if res.get("status") == "success":
                level = res["data"]["assessment"]["risk_level"]
                if level == "HIGH":
                    high_risk_count += 1
                elif level == "MEDIUM":
                    medium_risk_count += 1
                else:
                    low_risk_count += 1

        return {
            "status": "success",
            "code": 200,
            "timestamp": request_time,
            "data": {
                "total_analyzed": len(items),
                "summary": {
                    "high_risk_count": high_risk_count,
                    "medium_risk_count": medium_risk_count,
                    "low_risk_count": low_risk_count
                },
                "results": results
            }
        }


# Singleton service instance
_api_handler = JobRiskAPIHandler()


def analyze_job_posting(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Direct function interface for Python backend, Streamlit, and Orchestrator.
    Usage:
        from risk_engine import analyze_job_posting
        result = analyze_job_posting({"title": "...", "description": "..."})
    """
    return _api_handler.handle_assessment_request(payload)


def batch_analyze_job_postings(payload: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Batch processing function interface.
    Usage:
        from risk_engine import batch_analyze_job_postings
        results = batch_analyze_job_postings([job1, job2, job3])
    """
    return _api_handler.handle_batch_assessment_request(payload)
