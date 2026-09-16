/**
 * JobGuard AI - History View Renderer
 * 
 * Manages rendering of historical forensic audit logs, real-time search filtering,
 * and record inspection.
 * 
 * @module ui/renderers/historyView
 */

import { StorageService } from '../../services/storageService.js';
import { ResultsView } from './resultsView.js';
import { STORAGE_KEYS } from '../../config/constants.js';

export class HistoryView {
  static currentQuery = '';

  /**
   * Initializes event listeners for search input.
   */
  static init() {
    const searchInput = document.getElementById('historySearchInput') || document.getElementById('topSearch');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.currentQuery = e.target.value.toLowerCase().trim();
        this.render();
      });
    }
  }

  /**
   * Render the history entries into the DOM.
   */
  static render() {
    const container = document.getElementById('historyContainer');
    if (!container) return;

    let history = StorageService.getHistory();

    // 1. Search Query Filtering
    if (this.currentQuery) {
      const q = this.currentQuery;
      history = history.filter(item => {
        const title = (item.jobPosting?.title || item.title || '').toLowerCase();
        const comp = (item.jobPosting?.company || item.company || '').toLowerCase();
        const summary = (item.summary || '').toLowerCase();
        return title.includes(q) || comp.includes(q) || summary.includes(q);
      });
    }

    if (history.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 48px 20px; color: var(--text-faint);">
          <svg class="icon lg" style="margin: 0 auto 12px; width: 36px; height: 36px; stroke-width: 1.5;"><use href="#i-clock"/></svg>
          <div style="font-size: 14.5px; font-weight: 650; color: var(--text-muted); margin-bottom: 6px;">No analysis history yet</div>
          <div style="font-size: 12.5px; max-width: 320px; margin: 0 auto 16px; line-height: 1.5;">Every job posting you scan is saved locally in your private browser storage, just like ChatGPT.</div>
          <button class="btn-primary" style="margin: 0 auto; display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; font-size: 12.5px; border-radius: 999px;" onclick="document.querySelector('[data-page=new-analysis]').click()">
            <svg class="icon sm"><use href="#i-plus"/></svg> Analyze a Job Now
          </button>
        </div>
      `;
      return;
    }

    const groups = this._groupHistory(history);

    const levelChipStyle = {
      low: 'background:var(--green-soft); color:var(--green);',
      medium: 'background:var(--amber-soft); color:var(--amber);',
      high: 'background:var(--orange-soft); color:var(--orange);',
      critical: 'background:var(--critical-soft); color:var(--critical);'
    };

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 4px;">
        <span style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-faint);">Saved Scans (${history.length})</span>
        <button id="clearAllHistoryBtn" style="background: none; border: none; font-size: 11.5px; color: var(--red); cursor: pointer; font-weight: 600; padding: 4px 8px; border-radius: 4px;">Clear All</button>
        <button id="loadSampleBtn" style="background: var(--blue-soft); border: none; font-size: 11.5px; color: var(--blue); cursor: pointer; font-weight: 600; padding: 4px 8px; border-radius: 4px; margin-left:8px;">Load Sample History</button>
      </div>
      ${groups.map(group => `
        <div class="history-group-label">${group.label}</div>
        ${group.items.map(item => {
          const score = item.riskScore !== undefined ? item.riskScore : (item.score || 0);
          const level = (item.riskLevel || item.level || 'medium').toLowerCase();
          const title = item.title || item.jobPosting?.title || 'Job Assessment';
          const relativeTime = this._formatRelativeTime(item.timestamp);

          return `
            <div class="history-item-row" style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <button class="history-item" data-id="${item.id}" style="flex: 1; margin-bottom: 0;">
                <div class="history-score-chip" style="${levelChipStyle[level] || levelChipStyle.medium}">${score}</div>
                <div class="history-item-body">
                  <div class="history-item-title">${this._escapeHtml(title)}</div>
                  <div class="history-item-sub">${score}/100 &middot; ${level.toUpperCase()} RISK</div>
                </div>
                <div class="history-time">${relativeTime}</div>
              </button>
              <button class="delete-history-btn" data-id="${item.id}" title="Delete scan" style="background: transparent; border: 1px solid var(--border); border-radius: 8px; width: 34px; height: 38px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-faint); transition: all .15s ease;">
                <svg class="icon sm" style="width: 13px; height: 13px;"><use href="#i-x"/></svg>
              </button>
            </div>
          `;
        }).join('')}
      `).join('')}
    `;

    // Bind item click to load result
    container.querySelectorAll('.history-item').forEach(el => {
      el.addEventListener('click', () => {
        const id = el.dataset.id;
        const allHistory = StorageService.getHistory();
        const record = allHistory.find(r => r.id === id);
        if (record) {
          ResultsView.render(record);
          Router.navigate('results');
        }
      });
    });

    // Bind delete single scan
    container.querySelectorAll('.delete-history-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        StorageService.deleteReport(id);
        this.render();
      });
    });

    // Bind clear all
    const clearBtn = document.getElementById('clearAllHistoryBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all analysis history?')) {
          StorageService.clearHistory();
          this.render();
        }
      });
    }
    // Load Sample History button handler
    const loadSampleBtn = document.getElementById('loadSampleBtn');
    if (loadSampleBtn) {
      loadSampleBtn.addEventListener('click', () => {
        // Overwrite history with sample data
        const samples = HistoryView._sampleData();
        localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(samples));
        this.render();
      });
    }
  }

  /**
   * Returns sample history entries.
   */
  static _sampleData() {
    const now = Date.now();
    return [
      {
        id: 'JG_SAMPLE1',
        timestamp: new Date(now - 2 * 86400000).toISOString(),
        title: 'Senior Frontend Engineer',
        company: 'TechCorp',
        riskScore: 30,
        riskLevel: 'low',
        confidence: 95,
        summary: 'Low risk job posting.',
        breakdown: {},
        flags: [],
        recommendations: [],
        ai_assessment: null,
        rawText: 'sample job description 1',
        contact: 'hr@techcorp.com',
        url: 'https://techcorp.com/careers/123'
      },
      {
        id: 'JG_SAMPLE2',
        timestamp: new Date(now - 86400000).toISOString(),
        title: 'Payment Processing Specialist',
        company: 'FastPay',
        riskScore: 78,
        riskLevel: 'high',
        confidence: 92,
        summary: 'Potentially risky payment job.',
        breakdown: {},
        flags: [],
        recommendations: [],
        ai_assessment: null,
        rawText: 'sample job description 2',
        contact: 'jobs@fastpay.xyz',
        url: 'https://fastpay.xyz/jobs/456'
      },
      {
        id: 'JG_SAMPLE3',
        timestamp: new Date(now).toISOString(),
        title: 'Data Analyst',
        company: 'DataWorks',
        riskScore: 45,
        riskLevel: 'medium',
        confidence: 94,
        summary: 'Moderate risk.',
        breakdown: {},
        flags: [],
        recommendations: [],
        ai_assessment: null,
        rawText: 'sample job description 3',
        contact: 'recruit@dataworks.com',
        url: 'https://dataworks.com/jobs/789'
      }
    ];
  }

  /**
   * Ensure sample history is seeded if empty.
   */
  static ensureSampleHistory() {
    const history = StorageService.getHistory();
    if (!history || history.length === 0) {
      const samples = this._sampleData();
      localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(samples));
    }
  }


  /**
   * Groups items into Today, Yesterday, This Week, and Older.
   * @private
   */
  static _groupHistory(items) {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterdayStart = todayStart - 86400000;
    const weekStart = todayStart - 6 * 86400000;

    const today = [];
    const yesterday = [];
    const thisWeek = [];
    const older = [];

    items.forEach(item => {
      const time = new Date(item.timestamp || Date.now()).getTime();
      if (time >= todayStart) today.push(item);
      else if (time >= yesterdayStart) yesterday.push(item);
      else if (time >= weekStart) thisWeek.push(item);
      else older.push(item);
    });

    const groups = [];
    if (today.length > 0) groups.push({ label: 'TODAY', items: today });
    if (yesterday.length > 0) groups.push({ label: 'YESTERDAY', items: yesterday });
    if (thisWeek.length > 0) groups.push({ label: 'EARLIER THIS WEEK', items: thisWeek });
    if (older.length > 0) groups.push({ label: 'PREVIOUS SCANS', items: older });
    return groups;
  }

  /**
   * Formats a timestamp into human-readable relative time.
   * @private
   */
  static _formatRelativeTime(iso) {
    if (!iso) return 'Just now';
    const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 172800) return 'Yesterday';
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  static _escapeHtml(str) {
    return (str || '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
  }
  }
}
