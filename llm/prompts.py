ANALYSIS_PROMPT_TEMPLATE = """You are a job-scam risk analyst. Analyze the job posting below for signs of fraud that go beyond obvious keyword matches.

Job posting text:
\"\"\"
{job_text}
\"\"\"

Additional context:
- Contact email: {email}
- URL provided: {url}

SEVERITY CALIBRATION (follow strictly — this directly affects a numeric score downstream):
- "high": ONLY for concrete financial or data risk — requests for payment, bank/ID details,
  guaranteed/unrealistic income promises, or instructions to send money/crypto/gift cards.
- "medium": missing verifiable contact info, no named company, generic corporate-sounding
  email with no real domain, or a clear mismatch between the role and its described duties.
- "low": minor stylistic issues only — informal tone, brief description, below-market salary
  ALONE with no other red flag.
- Do NOT flag a posting as "high" or "medium" severity for things that are simply normal,
  slightly generic business writing (e.g. "we offer great benefits", a short job description,
  a real company name with a standard application process). Legitimate postings are often brief.
- If the posting names a specific company, describes a normal application/interview process,
  and shows no financial or data-risk red flag, your overall_impression should be positive/neutral
  and contextual_flags should be empty or near-empty — do not manufacture concerns to fill the list.

COMMON FALSE-POSITIVE TRAPS (do NOT flag these on their own):
- The word "urgent" or "urgent hiring" is NOT itself a scam signal. Real businesses hire urgently
  for real reasons (a project scale-up, a sudden vacancy, seasonal demand). Only flag urgency as
  "pressure_tactics" if it is paired with another concrete red flag (e.g. payment request, no
  verification possible, no real company name). If the posting gives a plausible business reason
  for urgency AND includes verifiable specifics (named location, named benefits like insurance/
  provident fund, a real interview step), treat the urgency as normal and do not flag it.
- A short or concise job description is NOT automatically "vague". Only flag
  "vague_role_description" if the posting truly gives no indication of what the work involves,
  what industry it's in, or how the hiring process works — not simply because it's brief.
- Mentioning specific, checkable details (a city, a named benefit like health insurance or EOBI,
  a named application step) is evidence AGAINST fraud, even in an urgent-sounding posting weigh
  this evidence when deciding whether to flag anything at all.

Instructions:
- Identify only genuine contextual red flags a keyword filter would miss.
- Do NOT assign a numeric risk score or risk level — that is handled separately.
- Rate your own certainty as "high", "medium", or "low".
- Respond with ONLY valid JSON, no other text, in exactly this format:

{{
  "contextual_flags": [
    {{"flag": "short flag name", "reasoning": "one sentence explanation", "severity": "low|medium|high"}}
  ],
  "overall_impression": "one or two sentence plain-language summary",
  "llm_certainty": "high|medium|low"
}}
"""

def build_analysis_prompt(job_text: str, email: str = None, url: str = None) -> str:
    return ANALYSIS_PROMPT_TEMPLATE.format(
        job_text=job_text.strip(),
        email=email or "not provided",
        url=url or "not provided"
    )