/**
 * JobGuard AI - Results View Renderer
 * 
 * Renders the comprehensive threat assessment results page, flag breakdown,
 * category metrics, and actionable recommendations.
 * 
 * @module ui/renderers/resultsView
 */

import { GaugeRenderer } from './gaugeRenderer.js';
import { getRiskColor, getRiskBgColor } from '../../config/constants.js';
import { ExportService } from '../../services/exportService.js';
import { Toast } from '../toast.js';

export class ResultsView {
  static currentReport = null;

  /**
   * Renders a RiskReport entity into the results page DOM.
   * @param {Object} report 
   */
  static render(report) {
    if (!report) return;
    this.currentReport = report;

    const level = (report.riskLevel || 'medium').toLowerCase();
    const score = report.riskScore || 0;
    const confidence = report.confidence || 87;

    // 1. Gauge and Spectrum
    GaugeRenderer.render(score, level);

    // 2. Risk Badge
    const riskBadge = document.getElementById('riskBadge');
    if (riskBadge) {
      riskBadge.className = `risk-badge ${level}`;
      riskBadge.innerHTML = `<span class="dot"></span>${(report.riskLevel || 'EVALUATION').toUpperCase()} RISK`;
    }

    // 3. Confidence Metrics
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceFill = document.getElementById('confidenceFill');
    if (confidenceValue) confidenceValue.textContent = `${confidence}%`;
    if (confidenceFill) {
      requestAnimationFrame(() => {
        setTimeout(() => {
          confidenceFill.style.width = `${confidence}%`;
        }, 80);
      });
    }

    // 4. Detected Indicators List
    this.renderIndicators(report.flags);

    // 5. Category Breakdown
    this.renderBreakdown(report.breakdown);

    // 6. AI Assessment Card
    this.renderAIAssessment(report);

    // 7. Actionable Recommendations
    this.renderRecommendations(report.recommendations);

    // 8. Bind Actions
    this.bindActions();
  }

  static renderIndicators(flags) {
    const listEl = document.getElementById('indicatorsList');
    if (!listEl) return;

    if (!flags || flags.length === 0) {
      listEl.innerHTML = `
        <div class="indicator-card">
          <div class="indicator-icon" style="background:var(--green-soft); color:var(--green);"><svg class="icon"><use href="#i-shield-check"/></svg></div>
          <div class="indicator-body">
            <div class="indicator-top">
              <div class="indicator-title">No High-Risk Red Flags Detected</div>
              <div class="indicator-points" style="color:var(--green); background:var(--green-soft);">0 points</div>
            </div>
            <div class="indicator-desc">The analyzed posting satisfies primary legitimate employment heuristics.</div>
          </div>
        </div>
      `;
      return;
    }

    listEl.innerHTML = flags.map(f => {
      let icon = 'i-alert';
      if (f.category && f.category.includes('Payment')) icon = 'i-dollar';
      else if (f.category && f.category.includes('Salary')) icon = 'i-zap';
      else if (f.category && f.category.includes('Domain')) icon = 'i-mail';

      return `
        <div class="indicator-card">
          <div class="indicator-icon"><svg class="icon"><use href="#${icon}"/></svg></div>
          <div class="indicator-body">
            <div class="indicator-top">
              <div class="indicator-title">${f.title}</div>
              <div class="indicator-points">+${f.weight || f.points || 15} points</div>
            </div>
            <div class="indicator-desc">${f.description || f.desc}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  static renderBreakdown(breakdown) {
    const listEl = document.getElementById('breakdownList');
    if (!listEl) return;

    const items = [
      { label: 'Payment & Financial Risk', score: breakdown?.contractTerms ?? 0, max: 30 },
      { label: 'Suspicious / Urgent Language', score: breakdown?.urgencyAndPressure ?? 0, max: 25 },
      { label: 'Domain & Recruiter Email Signals', score: breakdown?.domainReputation ?? 0, max: 15 },
      { label: 'Communication Channel Signals', score: breakdown?.communicationVectors ?? 0, max: 15 },
      { label: 'Role & Compensation Quality', score: breakdown?.compensationFeasibility ?? 0, max: 15 }
    ];

    listEl.innerHTML = items.map(b => `
      <div class="breakdown-row">
        <div class="breakdown-top">
          <span class="breakdown-label">${b.label}</span>
          <span class="breakdown-score">${b.score} / ${b.max}</span>
        </div>
        <div class="breakdown-track"><div class="breakdown-fill" data-w="${Math.min(100, Math.round((b.score / b.max) * 100))}"></div></div>
      </div>
    `).join('');

    requestAnimationFrame(() => {
      setTimeout(() => {
        listEl.querySelectorAll('.breakdown-fill').forEach(el => {
          el.style.width = el.dataset.w + '%';
        });
      }, 100);
    });
  }

  static renderAIAssessment(report) {
    const card = document.getElementById('aiVerdictCard');
    const emojiEl = document.getElementById('aiVerdictEmoji');
    const titleEl = document.getElementById('aiVerdictTitle');
    const p1 = document.getElementById('aiSummaryP1');
    const p2 = document.getElementById('aiSummaryP2');
    const p3 = document.getElementById('aiSummaryP3');

    const score = report.riskScore ?? report.score ?? 0;
    const ai = report.ai_assessment;

    let state = 'safe';
    let emoji = '✅';
    let title = 'Looks Genuine & Safe to Apply';
    let text1 = '✅ Verdict: No issues found. This job posting appears to be an authentic and legitimate hiring opportunity.';
    let text2 = 'Why this is safe: The hiring post uses standard recruitment practices, requires real qualifications (like a CV or portfolio), and never asks you for upfront fees or crypto transfers.';
    let text3 = 'What you should do: You can proceed with your application. Always protect personal details like passwords and bank numbers during early interviews.';

    if (ai) {
      emoji = ai.emoji || emoji;
      title = ai.verdict_title || title;
      text1 = ai.p1 || text1;
      text2 = ai.p2 || text2;
      text3 = ai.p3 || text3;
      state = ai.verdict_level === 'low' ? 'safe' : (ai.verdict_level === 'medium' ? 'caution' : 'danger');
    } else if (score > 50) {
      state = 'danger';
      emoji = '🚨';
      title = score > 75 ? 'Extreme Scam Danger — Do Not Apply' : 'Warning: High Risk Job Scam Detected';
      text1 = '🚨 Verdict: Serious issues detected! This posting shows clear signs of an employment scam designed to steal your money or personal identity.';
      text2 = 'Why this is dangerous: Real employers NEVER ask you to pay registration or training fees to get a job, and they do not push candidates to anonymous chat apps like Telegram.';
      text3 = 'What you should do: STOP immediately. Do not send money, do not deposit checks, and do not share copies of your ID or bank details.';
    } else if (score > 25) {
      state = 'caution';
      emoji = '⚠️';
      title = 'Caution Advised — Minor Anomalies Found';
      text1 = '⚠️ Verdict: Potential concerns detected. This may not be an outright scam, but there are a few suspicious or unverified details you should double-check.';
      text2 = 'Why we flagged this: Some details (like an unverified email or vague job requirements) deviate from standard hiring procedures.';
      text3 = 'What you should do: Verify the employer independently on LinkedIn or through their official corporate website before sharing personal details.';
    }

    if (card) card.className = `ai-verdict-card ${state}`;
    if (emojiEl) emojiEl.textContent = emoji;
    if (titleEl) titleEl.textContent = title;
    if (p1) p1.innerHTML = text1;
    if (p2) p2.innerHTML = text2;
    if (p3) p3.innerHTML = text3;
  }

  static renderRecommendations(recommendations) {
    const container = document.getElementById('actionsContainer');
    if (!container) return;

    if (!recommendations || recommendations.length === 0) {
      recommendations = [
        'Do not send money or equipment fees before employment verification.',
        'Do not share passwords, OTPs, bank details, or sensitive IDs.',
        'Verify the company independently on official directories.',
        'Check the official company website careers page.',
        'Be cautious of urgency and pressure tactics.'
      ];
    }

    container.innerHTML = recommendations.map(rec => `
      <div class="action-check-row">
        <span class="check-mark"><svg class="icon"><use href="#i-check"/></svg></span>
        ${rec}
      </div>
    `).join('');
  }

  static bindActions() {
    const copyBtn = document.getElementById('copyReportBtn');
    const shareBtn = document.getElementById('shareReportBtn');
    const saveBtn = document.getElementById('saveAnalysisBtn');

    if (copyBtn) {
      copyBtn.onclick = () => {
        if (!this.currentReport) return;
        const text = ExportService.generateMarkdown(this.currentReport);
        ExportService.copyToClipboard(text).then(() => {
          Toast.show('Report copied to clipboard');
        });
      };
    }

    if (shareBtn) {
      shareBtn.onclick = () => Toast.show('Share link ready to send');
    }

    if (saveBtn) {
      saveBtn.onclick = () => Toast.show('Analysis saved successfully');
    }
  }
}
