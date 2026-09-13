RULES = [
    {
        "id": "R001",
        "category": "payment",
        "keywords": ["registration fee", "processing fee", "training fee",
                     "deposit required", "pay to apply", "advance payment"],
        "weight": 10,
        "description": "Asks for upfront payment from applicant"
    },
    {
        "id": "R002",
        "category": "payment",
        "keywords": ["send money", "wire transfer", "gift card", "bitcoin", "crypto payment"],
        "weight": 10,
        "description": "Requests money transfer or crypto payment"
    },
    {
        "id": "R003",
        "category": "contact",
        "keywords": ["whatsapp only", "contact us on whatsapp", "telegram only"],
        "weight": 6,
        "description": "Communication restricted to informal channels only"
    },
    {
        "id": "R004",
        "category": "contact",
        "keywords": [],
        "weight": 5,
        "description": "Recruiter using free/generic email instead of company domain"
    },
    {
        "id": "R005",
        "category": "salary",
        "keywords": ["earn $5000 weekly", "guaranteed income", "no experience high salary",
                     "easy money", "get rich quick"],
        "weight": 8,
        "description": "Unrealistic salary or guaranteed high income claims"
    },
    {
        "id": "R006",
        "category": "process",
        "keywords": ["no interview required", "instant hiring", "immediate joining no interview",
                     "hired without interview"],
        "weight": 7,
        "description": "Skips normal hiring process (no interview)"
    },
    {
        "id": "R007",
        "category": "urgency",
        "keywords": ["urgent hiring", "limited seats", "apply within 24 hours",
                     "act now", "hurry limited time"],
        "weight": 5,
        "description": "Artificial urgency/pressure tactics"
    },
    {
        "id": "R008",
        "category": "financial_info",
        "keywords": ["send your bank details", "share your account number", "share your account details",
                     "provide your bank account", "account number and bank"],
        "weight": 8,
        "description": "Requests bank account details before any formal engagement"
    },
    {
        "id": "R009",
        "category": "grammar",
        "keywords": [],
        "weight": 3,
        "description": "Poor grammar / spelling density (heuristic check)"
    },
    {
        "id": "R010",
        "category": "vagueness",
        "keywords": ["work from home no skills needed", "any qualification accepted",
                     "no experience needed high pay"],
        "weight": 6,
        "description": "Overly vague job description with no real requirements"
    },
    {
        "id": "R011",
        "category": "identity_document",
        "keywords": ["cnic copy", "cnic number", "aadhar number", "aadhaar number",
                     "passport copy", "national id copy", "id card copy required"],
        "weight": 12,
        "description": "Requests a copy or number of a government-issued ID document"
    },
]