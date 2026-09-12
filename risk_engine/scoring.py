"""
Production-Grade Risk Scoring Algorithm for Job Risk Assessment.
Calculates normalized risk scores (0-100), determines risk classification,
applies non-linear escalation penalties, and generates actionable safety advice.
"""

from dataclasses import dataclass, asdict
from enum import Enum
import math
from typing import Any, Dict, List, Optional
from rules.red_flags import run_all_red_flags


class RiskLevel(str, Enum):
    LOW = "LOW"            # 0.0 - 29.9: Safe / Normal
    MEDIUM = "MEDIUM"      # 30.0 - 69.9: Suspicious / Proceed with Caution
    HIGH = "HIGH"          # 70.0 - 100.0: Critical Scam Probability


@dataclass
class RiskReport:
    overall_score: float                # 0.0 to 100.0
    risk_level: RiskLevel               # LOW, MEDIUM, HIGH
    confidence_score: float             # 0.0 to 1.0 (Assessment reliability)
    summary: str                        # Human-readable executive verdict
    total_violations_found: int         # Count of triggered rules
    category_breakdown: Dict[str, int]  # Weight per risk category
    violations: List[Dict[str, Any]]    # Details of each matched violation
    safety_recommendations: List[str]   # Prioritized safety guidelines

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["risk_level"] = self.risk_level.value
        return result


class RiskScoringEngine:
    """
    Evaluates raw rule findings through non-linear compound weighting,
    critical risk escalation, and information-density confidence scoring.
    """

    # Scoring constants
    CRITICAL_FLOOR: float = 75.0       # Any CRITICAL flag forces score >= 75
    HIGH_FLOOR: float = 45.0           # Any HIGH flag forces score >= 45
    COMPOUND_MULTIPLIER: float = 1.15  # Penalty when multiple distinct categories trigger

    def __init__(self, critical_floor: float = 75.0, high_floor: float = 45.0):
        self.critical_floor = critical_floor
        self.high_floor = high_floor

    def calculate_confidence(self, job_data: Dict[str, Any]) -> float:
        """
        Estimates the reliability of the assessment based on input completeness.
        More complete fields = higher confidence (0.4 to 0.98).
        """
        score = 0.40  # Baseline confidence

        # Title completeness
        title = (job_data.get("title") or "").strip()
        if len(title) >= 3:
            score += 0.10

        # Company provided
        company = (job_data.get("company") or "").strip()
        if len(company) >= 2:
            score += 0.15

        # Contact email provided
        contact = (job_data.get("contact_email") or "").strip()
        if "@" in contact:
            score += 0.15

        # Description depth
        desc = (job_data.get("description") or "").strip()
        word_count = len(desc.split())
        if word_count >= 100:
            score += 0.15
        elif word_count >= 40:
            score += 0.08

        # Salary info provided
        salary = (job_data.get("salary_text") or "").strip()
        if salary:
            score += 0.05

        return min(round(score, 2), 0.98)

    def evaluate_risk(self, job_data: Dict[str, Any]) -> RiskReport:
        """
        Executes red-flag rules, applies the scoring algorithm,
        and constructs the complete RiskReport.
        """
        # 1. Run all deterministic detection rules
        rules_output = run_all_red_flags(job_data)
        violations = rules_output["violations"]
        critical_count = rules_output["critical_count"]
        high_count = rules_output["high_count"]
        total_weight = rules_output["total_rule_weight"]

        # 2. Category Breakdown
        category_breakdown: Dict[str, int] = {}
        for v in violations:
            cat = v["category"]
            category_breakdown[cat] = category_breakdown.get(cat, 0) + v["weight"]

        # 3. Base Score Calculation with Multi-Category Escalation
        num_categories = len(category_breakdown)
        raw_score = float(total_weight)

        # Compound escalation: If multiple different categories triggered, amplify risk
        if num_categories >= 2:
            escalation_factor = 1.0 + (num_categories - 1) * 0.10
            raw_score = raw_score * escalation_factor

        # 4. Critical & High Floors (No legitimate job charges fees or uses money mules)
        if critical_count > 0:
            raw_score = max(raw_score, self.critical_floor)
        elif high_count > 0:
            raw_score = max(raw_score, self.high_floor)

        # Cap score between 0.0 and 100.0
        final_score = round(min(max(raw_score, 0.0), 100.0), 1)

        # 5. Risk Level Classification
        if final_score >= 70.0:
            level = RiskLevel.HIGH
            summary = (
                f"HIGH RISK SCAM ALERT: This job posting exhibits severe fraud indicators "
                f"({critical_count} critical, {high_count} high-severity violations). "
                f"Applying is strongly discouraged."
            )
        elif final_score >= 30.0:
            level = RiskLevel.MEDIUM
            summary = (
                f"MEDIUM RISK WARNING: Suspicious elements detected in communication "
                f"or identity verification. Exercise strict caution before sharing information."
            )
        else:
            level = RiskLevel.LOW
            summary = (
                "LOW RISK: No critical red flags detected. The posting appears consistent "
                "with standard recruitment practices."
            )

        # 6. Prioritized Safety Recommendations
        recommendations: List[str] = []
        if critical_count > 0:
            recommendations.append("DO NOT pay any upfront fees, wire money, or buy equipment from specified links.")
            recommendations.append("NEVER accept or forward packages from home (reshipping scam).")
        if any(v["rule_id"] == "RULE_SUSPICIOUS_COMMUNICATION_APP" for v in violations):
            recommendations.append("Request official email communication; do not conduct recruitment solely over Telegram/WhatsApp.")
        if any(v["rule_id"] == "RULE_FREE_PUBLIC_EMAIL_DOMAIN" for v in violations):
            recommendations.append("Verify the recruiter's credentials on LinkedIn or the corporate company website.")
        if any(v["rule_id"] == "RULE_PREMATURE_PII_HARVESTING" for v in violations):
            recommendations.append("Do not provide SSN, CNIC, ID scans, or banking details before a verified offer letter.")

        # Default recommendation if clean
        if not recommendations:
            recommendations.append("Follow standard safety practices: verify employer authenticity and company website.")

        # 7. Confidence Score
        confidence = self.calculate_confidence(job_data)

        return RiskReport(
            overall_score=final_score,
            risk_level=level,
            confidence_score=confidence,
            summary=summary,
            total_violations_found=len(violations),
            category_breakdown=category_breakdown,
            violations=violations,
            safety_recommendations=recommendations
        )


# Convenience function for quick scoring
_default_engine = RiskScoringEngine()

def calculate_job_risk(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for backend API and orchestration callers.
    Accepts job dictionary, returns serializable risk assessment report.
    """
    report = _default_engine.evaluate_risk(job_data)
    return report.to_dict()
