"""
v3: Added a hard-trigger override for identity-document requests (CNIC/Aadhaar/passport).
Requesting a government ID copy is categorically more severe than requesting bank account
details alone. Also switched from flat summing to diminishing-returns aggregation in
scorer.py, so MAX_TOTAL_WEIGHT here is a placeholder pending final tuning.
"""

MAX_TOTAL_WEIGHT = 40  # PLACEHOLDER — will finalize after seeing the diminishing-sum table

RISK_BANDS = [
    (0, 25, "Low"),
    (26, 50, "Medium"),
    (51, 75, "High"),
    (76, 100, "Critical"),
]

HARD_CRITICAL_CATEGORIES = {"identity_document"}
HARD_CRITICAL_FLOOR = 80