/**
 * @fileoverview Risk Assessment Scoring Engine
 * Executes heuristic rules, calculates normalized scores, computes confidence, and produces a RiskReport.
 */

import { HEURISTIC_RULES } from './ruleCatalog.js';
import { FREE_EMAIL_DOMAINS, SUSPICIOUS_TLDS, RISK_LEVELS, RISK_THRESHOLDS } from '../../config/constants.js';
import { RiskReport } from '../models/RiskReport.js';

export class ScorerEngine {
  /**
   * Evaluates a JobPosting entity against the rule taxonomy.
   * @param {import('../models/JobPosting.js').JobPosting} jobPosting
   * @returns {RiskReport}
   */
  static evaluate(jobPosting) {
    const fullText = `${jobPosting.title} ${jobPosting.company} ${jobPosting.rawText} ${jobPosting.recruiterEmail} ${jobPosting.jobUrl}`;
    const detectedIndicators = [];
    let cumulativeScore = 0;

    // 1. Evaluate Text Heuristic Rules
    for (const rule of HEURISTIC_RULES) {
      if (rule.regex.test(fullText)) {
        detectedIndicators.push({
          icon: rule.icon,
          title: rule.title,
          desc: rule.desc,
          points: rule.weight,
          category: rule.category
        });
        cumulativeScore += rule.weight;
      }
    }

    // 2. Evaluate Email Signals
    let emailSignalScore = 0;
    if (jobPosting.recruiterEmail) {
      const domain = jobPosting.recruiterEmail.split('@')[1]?.toLowerCase() || '';
      if (FREE_EMAIL_DOMAINS.includes(domain)) {
        detectedIndicators.push({
          icon: 'i-mail',
          title: 'Unverified Recruiter Mailbox',
          desc: `Recruiter uses a free public email provider (@${domain}) instead of corporate domain.`,
          points: 15,
          category: 'Email Signals'
        });
        emailSignalScore += 10;
        cumulativeScore += 15;
      }
    }

    // 3. Evaluate URL Signals
    let urlSignalScore = 0;
    if (jobPosting.jobUrl) {
      const isSuspicious = SUSPICIOUS_TLDS.some(tld => jobPosting.jobUrl.toLowerCase().includes(tld));
      if (isSuspicious) {
        detectedIndicators.push({
          icon: 'i-link',
          title: 'High-Risk Domain Extension',
          desc: 'Job URL uses a top-level domain frequently associated with deceptive landing pages.',
          points: 15,
          category: 'URL Signals'
        });
        urlSignalScore += 10;
        cumulativeScore += 15;
      }
    }

    // Normalized Final Score (0 - 100)
    const finalScore = Math.min(100, cumulativeScore);

    // Determine Risk Level
    let level = RISK_LEVELS.LOW;
    if (finalScore > RISK_THRESHOLDS.HIGH_MAX) {
      level = RISK_LEVELS.CRITICAL;
    } else if (finalScore > RISK_THRESHOLDS.MEDIUM_MAX) {
      level = RISK_LEVELS.HIGH;
    } else if (finalScore > RISK_THRESHOLDS.LOW_MAX) {
      level = RISK_LEVELS.MEDIUM;
    }

    // Confidence Calculation based on information richness
    let confidence = 75;
    if (jobPosting.rawText.length > 250) confidence += 10;
    if (jobPosting.recruiterEmail) confidence += 6;
    if (jobPosting.jobUrl) confidence += 6;
    confidence = Math.min(99, confidence);

    // Compute Category Breakdowns
    const breakdown = [
      {
        label: 'Payment Risk',
        score: Math.min(30, detectedIndicators.filter(i => i.category === 'Payment Risk').reduce((a, b) => a + b.points, 0)),
        max: 30
      },
      {
        label: 'Suspicious Language',
        score: Math.min(25, detectedIndicators.filter(i => i.category === 'Suspicious Language').reduce((a, b) => a + b.points, 0)),
        max: 25
      },
      {
        label: 'Email Signals',
        score: emailSignalScore > 0 ? 10 : 0,
        max: 15
      },
      {
        label: 'URL Signals',
        score: urlSignalScore > 0 ? 10 : 0,
        max: 15
      },
      {
        label: 'Information Quality',
        score: Math.min(15, detectedIndicators.filter(i => i.category === 'Information Quality').reduce((a, b) => a + b.points, 0)),
        max: 15
      }
    ];

    // Formulate AI Summary
    let aiSummary = '';
    if (level === RISK_LEVELS.CRITICAL || level === RISK_LEVELS.HIGH) {
      aiSummary = `This job posting contains several indicators commonly associated with suspicious job offers.\n\nThe strongest concerns are the request for upfront payment, unusually high earnings claims, and urgency-based language.\n\nHowever, JobGuard cannot confirm that this posting is fraudulent. The assessment represents an estimated risk based on the available information.`;
    } else if (level === RISK_LEVELS.MEDIUM) {
      aiSummary = `This job posting exhibits moderate risk indicators. We recommend verifying the recruiter's credentials and ensuring all communications occur through official channels.`;
    } else {
      aiSummary = `This job posting exhibits a low risk profile with realistic requirements and conventional recruitment phrasing. Always exercise standard precautions when applying.`;
    }

    const actionItems = [
      'Do not send money before employment verification.',
      'Do not share passwords, OTPs, bank details, or sensitive documents.',
      'Verify the company independently.',
      'Check the official company website.',
      'Be cautious of urgency and pressure tactics.'
    ];

    return new RiskReport({
      jobPosting,
      score: finalScore,
      level,
      confidence,
      indicators: detectedIndicators,
      breakdown,
      aiSummary,
      actionItems
    });
  }
}
