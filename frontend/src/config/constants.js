/**
 * @fileoverview JobGuard Domain Constants & Reference Lookups
 * @author JobGuard Engineering Team
 */

export const RISK_LEVELS = Object.freeze({
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
});

export const RISK_THRESHOLDS = Object.freeze({
  LOW_MAX: 25,
  MEDIUM_MAX: 50,
  HIGH_MAX: 75,
  CRITICAL_MAX: 100
});

export const RISK_COLORS = Object.freeze({
  [RISK_LEVELS.LOW]: 'var(--green)',
  [RISK_LEVELS.MEDIUM]: 'var(--amber)',
  [RISK_LEVELS.HIGH]: 'var(--orange)',
  [RISK_LEVELS.CRITICAL]: 'var(--critical)'
});

export const FREE_EMAIL_DOMAINS = Object.freeze([
  'gmail.com',
  'yahoo.com',
  'hotmail.com',
  'outlook.com',
  'proton.me',
  'protonmail.com',
  'aol.com',
  'mail.com',
  'icloud.com',
  'zoho.com'
]);

export const SUSPICIOUS_TLDS = Object.freeze([
  '.xyz',
  '.top',
  '.click',
  '.buzz',
  '.club',
  '.work',
  '.loan',
  '.link',
  '.gq',
  '.cf',
  '.tk',
  '.ml'
]);

export const STORAGE_KEYS = Object.freeze({
  HISTORY: 'jobguard_history',
  THEME: 'jobguard_theme',
  SETTINGS: 'jobguard_settings'
});
