/**
 * @fileoverview Application Storage Service
 * Manages persistent storage of scan reports in browser localStorage like ChatGPT / Claude.
 */

import { STORAGE_KEYS } from '../config/constants.js';

export class StorageService {
  /**
   * Retrieves all historical reports (flat array, newest first).
   * @returns {Array<Object>}
   */
  static getHistory() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.HISTORY);
      if (!data) return [];
      const parsed = JSON.parse(data);
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      console.warn('StorageService: Error reading history', e);
      return [];
    }
  }

  /**
   * Saves a new report to history (persists in localStorage).
   * @param {Object} report
   * @param {Object} [posting]
   * @returns {Object} saved record
   */
  static saveReport(report, posting = null) {
    try {
      const history = this.getHistory();
      const rawText = posting?.text || posting?.rawText || report.text || '';
      const email = posting?.contact || posting?.recruiterEmail || report.contact || '';
      const url = posting?.url || posting?.jobUrl || report.url || '';

      const title = this._extractTitle(rawText, email);
      const company = this._extractCompany(rawText, email);

      const record = {
        id: report.id || 'JG-' + Math.random().toString(36).substring(2, 9).toUpperCase(),
        timestamp: report.timestamp || new Date().toISOString(),
        title: report.title || title,
        company: report.company || company,
        riskScore: typeof report.riskScore === 'number' ? report.riskScore : (report.score ?? 0),
        riskLevel: (report.riskLevel || report.level || 'low').toLowerCase(),
        confidence: report.confidence || 95,
        summary: report.summary || '',
        breakdown: report.breakdown || {},
        flags: report.flags || report.indicators || [],
        recommendations: report.recommendations || report.actionItems || [],
        ai_assessment: report.ai_assessment || null,
        rawText,
        contact: email,
        url
      };

      // Avoid duplicate consecutive saves of the same scan
      if (history.length > 0 && history[0].rawText === rawText && Math.abs(new Date(history[0].timestamp) - new Date(record.timestamp)) < 5000) {
        return history[0];
      }

      history.unshift(record);
      // Cap at 100 scans to preserve localStorage quota
      if (history.length > 100) history.pop();

      localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history));
      return record;
    } catch (e) {
      console.warn('StorageService: Failed to persist report', e);
      return null;
    }
  }

  /**
   * Deletes a single scan by ID.
   * @param {string} id
   */
  static deleteReport(id) {
    try {
      const history = this.getHistory().filter(item => item.id !== id);
      localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history));
    } catch (e) {
      console.warn('StorageService: Failed to delete report', e);
    }
  }

  /**
   * Clears all scan history.
   */
  static clearHistory() {
    try {
      localStorage.removeItem(STORAGE_KEYS.HISTORY);
    } catch (e) {
      console.warn('StorageService: Failed to clear history', e);
    }
  }

  /**
   * Derives a clean job title from text.
   * @private
   */
  static _extractTitle(text, email = '') {
    if (!text) return 'Job Analysis Report';
    const lines = text.split('\n').map(l => l.replace(/[#*!|📊🎨📌⚡💰🏡🇺🇸⏰📩]/g, '').trim()).filter(Boolean);
    for (const l of lines) {
      if (l.length >= 4 && l.length <= 70) {
        return l;
      }
    }
    return lines[0]?.substring(0, 60) || 'Job Analysis Report';
  }

  /**
   * Extracts company name from email or text.
   * @private
   */
  static _extractCompany(text, email = '') {
    if (email && email.includes('@')) {
      const domain = email.split('@')[1].split('.')[0];
      if (!['gmail', 'yahoo', 'hotmail', 'outlook', 'proton', 'icloud'].includes(domain.toLowerCase())) {
        return domain.charAt(0).toUpperCase() + domain.slice(1);
      }
    }
    const match = text.match(/(?:at|company|hiring|team)\s+([A-Z][a-zA-Z0-9&]+)/i);
    return match ? match[1] : '';
  }
}
