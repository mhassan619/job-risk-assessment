"""
Verification Module for Job Risk Assessment.
Validates final assessment outputs for data integrity, completeness,
expected field presence, and score range sanity before returning to caller.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("Verification")
logger.setLevel(logging.INFO)

EXPECTED_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
VALID_VIOLATION_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


class AssessmentVerificationError(Exception):
    """Raised when a final assessment report fails integrity checks."""
    def __init__(self, message: str, issues: List[str]):
        super().__init__(message)
        self.issues = issues


def verify_assessment_report(report: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Runs a full structural and value-range integrity check on a completed assessment report.

    Returns:
        (is_valid: bool, issues: List[str])
    """
    issues: List[str] = []

    # 1. Top-level status must be success
    if report.get("status") != "success":
        issues.append(f"Report status is not 'success': {report.get('status')}")
        return False, issues

    assessment = report.get("risk_assessment") or report.get("assessment")
    if not assessment:
        issues.append("Missing 'risk_assessment' block in report.")
        return False, issues

    # 2. Overall score range check (0.0 - 100.0)
    score = assessment.get("overall_score")
    if score is None:
        issues.append("'overall_score' field is missing.")
    elif not isinstance(score, (int, float)):
        issues.append(f"'overall_score' must be numeric, got: {type(score).__name__}.")
    elif not (0.0 <= float(score) <= 100.0):
        issues.append(f"'overall_score' out of range: {score}. Expected 0.0 to 100.0.")

    # 3. Risk level must be a valid enum value
    risk_level = assessment.get("risk_level")
    if risk_level not in EXPECTED_RISK_LEVELS:
        issues.append(f"Invalid 'risk_level': '{risk_level}'. Expected one of {EXPECTED_RISK_LEVELS}.")

    # 4. Confidence score range (0.0 - 1.0)
    confidence = assessment.get("confidence_score")
    if confidence is not None:
        if not isinstance(confidence, (int, float)):
            issues.append("'confidence_score' must be numeric.")
        elif not (0.0 <= float(confidence) <= 1.0):
            issues.append(f"'confidence_score' out of range: {confidence}. Expected 0.0 to 1.0.")

    # 5. Violations structure check
    violations = assessment.get("violations", [])
    if not isinstance(violations, list):
        issues.append("'violations' must be a list.")
    else:
        for idx, v in enumerate(violations):
            if not isinstance(v, dict):
                issues.append(f"Violation at index {idx} is not a dict.")
                continue
            for required_key in ("rule_id", "severity", "weight", "message"):
                if required_key not in v:
                    issues.append(f"Violation {idx} missing required field: '{required_key}'.")
            if v.get("severity") not in VALID_VIOLATION_SEVERITIES:
                issues.append(f"Violation {idx} has invalid severity: '{v.get('severity')}'.")
            if not isinstance(v.get("weight"), (int, float)):
                issues.append(f"Violation {idx} 'weight' must be numeric.")

    # 6. Score-to-level consistency check
    if score is not None and risk_level in EXPECTED_RISK_LEVELS:
        fs = float(score)
        if risk_level == "HIGH" and fs < 70.0:
            issues.append(
                f"Inconsistency: risk_level is 'HIGH' but overall_score is {fs} (expected >= 70.0)."
            )
        elif risk_level == "MEDIUM" and not (30.0 <= fs < 70.0):
            issues.append(
                f"Inconsistency: risk_level is 'MEDIUM' but overall_score is {fs} (expected 30.0–69.9)."
            )
        elif risk_level == "LOW" and fs >= 30.0:
            issues.append(
                f"Inconsistency: risk_level is 'LOW' but overall_score is {fs} (expected < 30.0)."
            )

    # 7. Safety recommendations must exist
    recs = assessment.get("safety_recommendations")
    if not recs or not isinstance(recs, list) or len(recs) == 0:
        issues.append("'safety_recommendations' is missing or empty.")

    is_valid = len(issues) == 0
    if is_valid:
        logger.info("Assessment report passed all verification checks.")
    else:
        logger.warning("Assessment report failed verification: %s", issues)

    return is_valid, issues


def verify_and_enforce(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies the report and raises AssessmentVerificationError if invalid.
    Returns the original report unchanged if verification passes.
    """
    is_valid, issues = verify_assessment_report(report)
    if not is_valid:
        raise AssessmentVerificationError(
            "Assessment report failed integrity verification.",
            issues=issues
        )
    return report
