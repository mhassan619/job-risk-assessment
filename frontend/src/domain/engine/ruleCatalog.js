/**
 * @fileoverview Heuristic Threat Signature Catalog
 * Formal taxonomy of weighted scam indicators across payment, channel, compensation, urgency, and identity dimensions.
 */

export const HEURISTIC_RULES = Object.freeze([
  // 1. Payment & Upfront Financial Exploits
  {
    id: 'upfront_fee',
    category: 'Payment Risk',
    icon: 'i-dollar',
    title: 'Upfront Payment Requested',
    desc: 'The posting requests money before employment verification (registration, onboarding, or training fee).',
    weight: 30,
    regex: /(registration fee|training fee|processing fee|onboarding fee|background check fee|equipment fee|pay\s+\$?\d+|send\s+\$?\d+|fee is required|deposit required|one-time fee)/i
  },
  {
    id: 'crypto_wire',
    category: 'Payment Risk',
    icon: 'i-dollar',
    title: 'Untraceable Payment Channel',
    desc: 'Requests or promises transactions via Bitcoin, USDT, Crypto wallet, Zelle, CashApp, or Western Union.',
    weight: 35,
    regex: /(bitcoin|crypto|usdt|btc|ethereum|zelle|cashapp|cash app|venmo|western union|moneygram|gift card)/i
  },
  {
    id: 'check_cashing',
    category: 'Payment Risk',
    icon: 'i-dollar',
    title: 'Check Cashing / Vendor Purchase Scheme',
    desc: 'Promises to send a check to purchase home office equipment or supplies from a designated vendor.',
    weight: 35,
    regex: /(send you a check|mail you a check|deposit the check|cash the check|purchase equipment from our vendor|buy home office supplies)/i
  },

  // 2. Unrealistic Compensation & Role Anomalies
  {
    id: 'unrealistic_salary',
    category: 'Suspicious Language',
    icon: 'i-zap',
    title: 'Unrealistic Salary Claim',
    desc: 'Salary appears unusually high compared with the minimal role prerequisites ($8,000/mo or $85/hr for data entry).',
    weight: 25,
    regex: /(\$(?:[5-9]\d|\d{3,})\/hr|\$(?:[5-9],\d{3}|\d{5,})\/(?:week|month)|earn \$\d+ (daily|weekly)|no experience (needed|required)|earn from home \$\d+|make \$\d+ a (day|week))/i
  },

  // 3. Urgency & Coercion
  {
    id: 'urgency_manipulation',
    category: 'Suspicious Language',
    icon: 'i-alert',
    title: 'Urgency Manipulation',
    desc: 'The posting uses high-pressure, artificial scarcity, or urgency-based language.',
    weight: 15,
    regex: /(urgent hiring|immediate start|limited (positions|spots|slots)|apply (today|immediately|now)|act fast|reply within 24 hours|offer expires today)/i
  },

  // 4. Contact Channels & Messaging
  {
    id: 'telegram_interview',
    category: 'Suspicious Language',
    icon: 'i-mail',
    title: 'Instant Messaging Only Interview',
    desc: 'Candidate is instructed to contact someone via Telegram, WhatsApp, or text-only questionnaire.',
    weight: 20,
    regex: /(contact (us|me) on telegram|telegram handle|telegram app|interview on telegram|whatsapp interview|contact on whatsapp|signal app|text only interview)/i
  },

  // 5. Premature Identity Harvesting
  {
    id: 'pii_harvesting',
    category: 'Information Quality',
    icon: 'i-shield',
    title: 'Premature Identity & PII Request',
    desc: 'Asks for copies of government ID, passport, SSN, or bank credentials before a formal contract.',
    weight: 25,
    regex: /(copy of your id|driver'?s license (photo|copy)|send your passport|ssn|social security number|bank account details|routing number)/i
  }
]);
