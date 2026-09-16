/**
 * JobGuard AI - Analytics Service
 * 
 * Computes aggregate telemetry, statistical metrics, risk distributions,
 * and temporal trends from scanned job posting histories.
 * 
 * @module services/analyticsService
 */

import { StorageService } from './storageService.js';
import { RISK_LEVELS } from '../config/constants.js';

export class AnalyticsService {
  /**
   * Calculate comprehensive analytical metrics from storage history.
   * @param {Array<Object>} [records] Optional records override; defaults to storage history.
   * @returns {Object} Comprehensive analytics summary
   */
  static getMetrics(records = null) {
    const history = records || StorageService.getHistory();
    const totalScans = history.length;

    if (totalScans === 0) {
      return {
        totalScans: 0,
        averageRiskScore: 0,
        highRiskCount: 0,
        criticalRiskCount: 0,
        safeCount: 0,
        suspiciousCount: 0,
        distribution: {
          [RISK_LEVELS.SAFE]: 0,
          [RISK_LEVELS.LOW]: 0,
          [RISK_LEVELS.MEDIUM]: 0,
          [RISK_LEVELS.HIGH]: 0,
          [RISK_LEVELS.CRITICAL]: 0
        },
        distributionPercentages: {
          [RISK_LEVELS.SAFE]: 0,
          [RISK_LEVELS.LOW]: 0,
          [RISK_LEVELS.MEDIUM]: 0,
          [RISK_LEVELS.HIGH]: 0,
          [RISK_LEVELS.CRITICAL]: 0
        },
        mostCommonCategory: 'None Detected Yet'
      };
    }

    let scoreSum = 0;
    const distribution = {
      [RISK_LEVELS.SAFE]: 0,
      [RISK_LEVELS.LOW]: 0,
      [RISK_LEVELS.MEDIUM]: 0,
      [RISK_LEVELS.HIGH]: 0,
      [RISK_LEVELS.CRITICAL]: 0
    };

    const categoryCounts = {};

    history.forEach((item) => {
      const score = typeof item.riskScore === 'number' ? item.riskScore : (item.score || 0);
      scoreSum += score;

      const level = item.riskLevel || item.level || RISK_LEVELS.LOW;
      if (distribution[level] !== undefined) {
        distribution[level]++;
      } else {
        distribution[RISK_LEVELS.MEDIUM]++;
      }

      // Track flag categories if present
      if (Array.isArray(item.flags)) {
        item.flags.forEach(flag => {
          const cat = flag.category || 'General';
          categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });
      }
    });

    const averageRiskScore = Math.round(scoreSum / totalScans);
    const highRiskCount = (distribution[RISK_LEVELS.HIGH] || 0) + (distribution[RISK_LEVELS.CRITICAL] || 0);
    const safeCount = (distribution[RISK_LEVELS.SAFE] || 0) + (distribution[RISK_LEVELS.LOW] || 0);
    const suspiciousCount = distribution[RISK_LEVELS.MEDIUM] || 0;

    const distributionPercentages = {};
    Object.keys(distribution).forEach((key) => {
      distributionPercentages[key] = Math.round((distribution[key] / totalScans) * 100);
    });

    let mostCommonIndicator = totalScans > 0 ? 'No Scam Flags Detected' : 'None Detected Yet';
    let maxIndicatorCount = 0;
    const indicatorCounts = {};

    history.forEach(item => {
      const flags = item.flags || item.indicators || [];
      if (Array.isArray(flags)) {
        flags.forEach(flag => {
          const title = flag.title || flag.name || flag.category || 'Unknown Signal';
          indicatorCounts[title] = (indicatorCounts[title] || 0) + 1;
        });
      }
    });

    Object.entries(indicatorCounts).forEach(([title, count]) => {
      if (count > maxIndicatorCount) {
        maxIndicatorCount = count;
        mostCommonIndicator = title;
      }
    });

    return {
      totalScans,
      averageRiskScore,
      highRiskCount: (distribution[RISK_LEVELS.HIGH] || 0),
      criticalRiskCount: (distribution[RISK_LEVELS.CRITICAL] || 0),
      safeCount,
      suspiciousCount,
      distribution,
      distributionPercentages,
      mostCommonCategory: mostCommonIndicator
    };
  }
}
