"""
Risk Engine Package
Contains the scoring algorithm, confidence estimator, and backend API handler.
"""

from risk_engine.scoring import (
    calculate_job_risk,
    RiskScoringEngine,
    RiskReport,
    RiskLevel
)
from risk_engine.api_handler import (
    JobRiskAPIHandler,
    APIValidationError,
    analyze_job_posting,
    batch_analyze_job_postings
)

__all__ = [
    "calculate_job_risk",
    "RiskScoringEngine",
    "RiskReport",
    "RiskLevel",
    "JobRiskAPIHandler",
    "APIValidationError",
    "analyze_job_posting",
    "batch_analyze_job_postings"
]
