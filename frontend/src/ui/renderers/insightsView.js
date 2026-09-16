/**
 * JobGuard AI - Insights View Renderer
 * 
 * Computes and renders aggregate threat landscape statistics, telemetry charts,
 * risk distributions, and behavioral insights.
 * 
 * @module ui/renderers/insightsView
 */

import { AnalyticsService } from '../../services/analyticsService.js';
import { RISK_LEVELS } from '../../config/constants.js';

export class InsightsView {
  /**
   * Renders aggregate metrics into the DOM.
   */
  static render() {
    const metrics = AnalyticsService.getMetrics();

    // 1. Metric Stat Cards
    const totalScansEl = document.getElementById('statTotalScans');
    const avgScoreEl = document.getElementById('statAvgScore');
    const highRiskEl = document.getElementById('statHighRisk');
    const criticalRiskEl = document.getElementById('statCriticalRisk');
    const topIndicatorEl = document.getElementById('statTopIndicator');

    if (totalScansEl) totalScansEl.textContent = metrics.totalScans;
    if (avgScoreEl) avgScoreEl.textContent = metrics.averageRiskScore;
    if (highRiskEl) highRiskEl.textContent = metrics.highRiskCount;
    if (criticalRiskEl) criticalRiskEl.textContent = metrics.criticalRiskCount;
    if (topIndicatorEl) topIndicatorEl.textContent = metrics.mostCommonCategory;

    // 2. Risk Distribution
    const distContainer = document.getElementById('distributionList');
    if (distContainer) {
      const total = metrics.totalScans || 1;
      const lowCount = (metrics.distribution[RISK_LEVELS.SAFE] || 0) + (metrics.distribution[RISK_LEVELS.LOW] || 0);
      const medCount = metrics.distribution[RISK_LEVELS.MEDIUM] || 0;
      const highCount = metrics.distribution[RISK_LEVELS.HIGH] || 0;
      const critCount = metrics.distribution[RISK_LEVELS.CRITICAL] || 0;

      const data = [
        { label: 'Low', count: lowCount, max: total, color: 'var(--green)' },
        { label: 'Medium', count: medCount, max: total, color: 'var(--amber)' },
        { label: 'High', count: highCount, max: total, color: 'var(--orange)' },
        { label: 'Critical', count: critCount, max: total, color: 'var(--critical)' }
      ];

      distContainer.innerHTML = data.map(d => {
        const pct = metrics.totalScans > 0 ? Math.round((d.count / total) * 100) : 0;
        return `
          <div class="distribution-row">
            <span class="distribution-label">${d.label}</span>
            <div class="distribution-track"><div class="distribution-fill" data-w="${pct}" style="background:${d.color}; width:0%"></div></div>
            <span class="distribution-count">${d.count} (${pct}%)</span>
          </div>
        `;
      }).join('');

      requestAnimationFrame(() => {
        setTimeout(() => {
          distContainer.querySelectorAll('.distribution-fill').forEach(el => {
            el.style.width = el.dataset.w + '%';
          });
        }, 80);
      });
    }
  }
}
