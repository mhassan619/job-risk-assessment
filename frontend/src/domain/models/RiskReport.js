/**
 * @fileoverview Domain Entity representing an immutable Risk Assessment Report.
 */

import { RISK_LEVELS } from '../../config/constants.js';

export class RiskReport {
  /**
   * @param {Object} params
   * @param {string} params.id
   * @param {string} params.timestamp
   * @param {JobPosting} params.jobPosting
   * @param {number} params.score - 0 to 100
   * @param {string} params.level - 'low' | 'medium' | 'high' | 'critical'
   * @param {number} params.confidence - 0 to 100 percentage
   * @param {Array<Object>} params.indicators - Detected threat indicators
   * @param {Array<Object>} params.breakdown - Categorized score distributions
   * @param {string} params.aiSummary - Plain-English explanation
   * @param {Array<string>} params.actionItems - Recommended safety checklist
   */
  constructor({
    id = 'scan_' + Date.now(),
    timestamp = new Date().toISOString(),
    jobPosting,
    score = 0,
    level = RISK_LEVELS.LOW,
    confidence = 85,
    indicators = [],
    breakdown = [],
    aiSummary = '',
    actionItems = []
  }) {
    this.id = id;
    this.timestamp = timestamp;
    this.jobPosting = jobPosting;
    this.score = Math.min(100, Math.max(0, Math.round(score)));
    this.level = level;
    this.confidence = Math.min(100, Math.max(0, Math.round(confidence)));
    this.indicators = Object.freeze([...indicators]);
    this.breakdown = Object.freeze([...breakdown]);
    this.aiSummary = aiSummary;
    this.actionItems = Object.freeze([...actionItems]);

    Object.freeze(this);
  }

  /**
   * Serializes the entity to a plain JSON-safe object.
   * @returns {Object}
   */
  toJSON() {
    return {
      id: this.id,
      timestamp: this.timestamp,
      title: this.jobPosting?.title || 'Job Analysis',
      company: this.jobPosting?.company || '',
      score: this.score,
      level: this.level,
      confidence: this.confidence,
      indicators: this.indicators,
      breakdown: this.breakdown,
      aiSummary: this.aiSummary,
      actionItems: this.actionItems
    };
  }
}
