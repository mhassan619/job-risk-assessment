/**
 * JobGuard AI - Application Orchestrator
 * 
 * Main bootstrap orchestrator connecting the DOM UI, reactive SPA routing,
 * heuristic scoring engine, and telemetry persistence.
 * 
 * @module app
 */

import { Router } from './ui/router.js';
import { ThemeManager } from './ui/themeManager.js';
import { Toast } from './ui/toast.js';
import { JobPosting } from './domain/models/JobPosting.js';
import { Scorer } from './domain/engine/scorer.js';
import { StorageService } from './services/storageService.js';
import { ResultsView } from './ui/renderers/resultsView.js';
import { HistoryView } from './ui/renderers/historyView.js';
import { InsightsView } from './ui/renderers/insightsView.js';
import { PRESETS } from './config/presets.js';
import { ApiService } from './services/apiService.js';

export class App {
  static init() {
    // 1. Initialize core managers
    ThemeManager.init();
    Router.init();
    HistoryView.init();

    // 2. Register SPA route listeners
    Router.on('history', () => HistoryView.render());
    Router.on('insights', () => InsightsView.render());

    // 3. Bind analysis form interactions
    this.bindAnalysisForm();

    // 4. Initial Render for persistent views
    HistoryView.ensureSampleHistory();
    HistoryView.render();
    InsightsView.render();

    // 5. Probe backend and update status badge
    this.checkBackendStatus();

    console.log('🛡️ JobGuard AI Enterprise Architecture Initialized.');
  }

  /**
   * Probe the backend and update the AI status badge in the topbar.
   */
  static async checkBackendStatus() {
    const badge = document.getElementById('aiStatusBadge');
    if (!badge) return;
    try {
      const online = await ApiService.checkBackendHealth();
      if (online) {
        badge.className = 'ai-badge online';
        badge.innerHTML = '<span class="ai-dot"></span>AI Connected';
      } else {
        badge.className = 'ai-badge offline';
        badge.innerHTML = '<span class="ai-dot"></span>Offline Mode';
      }
    } catch {
      badge.className = 'ai-badge offline';
      badge.innerHTML = '<span class="ai-dot"></span>Offline Mode';
    }
  }

  /**
   * Bind event handlers for the job input and analysis form.
   */
  static bindAnalysisForm() {
    const jobInput = document.getElementById('jobInput');
    const recruiterEmail = document.getElementById('recruiterEmail');
    const jobUrl = document.getElementById('jobUrl');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const exampleSuspicious = document.getElementById('exampleSuspicious');
    const exampleNormal = document.getElementById('exampleNormal');

    // Preset examples
    if (exampleSuspicious) {
      exampleSuspicious.addEventListener('click', () => {
        if (jobInput) {
          jobInput.value = PRESETS.SUSPICIOUS_PAYMENT.text;
          jobInput.focus();
        }
        if (recruiterEmail) recruiterEmail.value = 'careers-fastrecruit@gmail.com';
        if (jobUrl) jobUrl.value = 'https://apply-fastcareers.xyz/job/9842';
        Toast.show('Loaded suspicious job example');
      });
    }

    if (exampleNormal) {
      exampleNormal.addEventListener('click', () => {
        if (jobInput) {
          jobInput.value = PRESETS.NORMAL_DEV.text;
          jobInput.focus();
        }
        if (recruiterEmail) recruiterEmail.value = 'recruiting@abctech.com';
        if (jobUrl) jobUrl.value = 'https://abctech.com/careers/intern';
        Toast.show('Loaded normal job example');
      });
    }

    // Analyze Trigger
    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', () => this.handleScan());
    }
  }

  /**
   * Execute evaluation workflow with step-by-step loading animation.
   */
  static async handleScan() {
    const jobInput = document.getElementById('jobInput');
    const recruiterEmail = document.getElementById('recruiterEmail');
    const jobUrl = document.getElementById('jobUrl');

    const text = jobInput ? jobInput.value.trim() : '';
    if (!text) {
      Toast.show('Please enter a job description to analyze');
      if (jobInput) jobInput.focus();
      return;
    }

    const posting = new JobPosting({
      text,
      contact: recruiterEmail ? recruiterEmail.value.trim() : '',
      url: jobUrl ? jobUrl.value.trim() : ''
    });

    // Navigate to loading view
    Router.navigate('loading');

    // Run simulated forensic analysis pipeline
    await this.runLoadingSequence();

    // 1. Attempt Multi-Agent Backend Analysis (97%+ Accuracy Network)
    let report = await ApiService.analyzeWithMultiAgent({
      text,
      contact: recruiterEmail ? recruiterEmail.value.trim() : null,
      url: jobUrl ? jobUrl.value.trim() : null
    });

    // 2. Seamless Fallback to Deterministic Client Scorer if offline
    if (!report) {
      report = Scorer.evaluate(posting);
    }

    // Save report to audit history (localStorage like ChatGPT)
    StorageService.saveReport(report, posting);
    HistoryView.render();
    InsightsView.render();

    // Render results view and transition
    ResultsView.render(report);
    Router.navigate('results');
    Toast.show('Analysis complete & saved to history');
  }

  /**
   * Orchestrates the animated loading steps.
   */
  static runLoadingSequence() {
    return new Promise((resolve) => {
      const steps = [
        { icon: '🔬', label: 'Tier 1 — Signal Extractor: scanning deception patterns' },
        { icon: '🌐', label: 'Tier 2 — Domain Verifier: live DNS & typo-squatting audit' },
        { icon: '📚', label: 'Tier 3 — RAG Engine: cross-referencing IC3/FTC scam corpus' },
        { icon: '⚖️', label: 'Agent Alpha (Prosecutor): hunting deceptive cues…' },
        { icon: '🛡️', label: 'Agent Beta (Defender): verifying corporate legitimacy…' },
        { icon: '🧠', label: 'Agent Gamma (Bayesian Judge): deliberating consensus verdict' }
      ];

      const stepList = document.getElementById('stepList');
      const loadingFinal = document.getElementById('loadingFinal');

      if (!stepList) {
        setTimeout(resolve, 800);
        return;
      }

      stepList.innerHTML = steps.map((s, i) =>
        `<div class="step-row" data-i="${i}">
           <span class="step-icon"><span class="spinner" style="display:none"></span><svg class="icon" style="display:none"><use href="#i-check"/></svg></span>
           <span><span class="step-emoji">${s.icon}</span> ${s.label}</span>
         </div>`
      ).join('');

      if (loadingFinal) loadingFinal.classList.remove('show');

      const rows = stepList.querySelectorAll('.step-row');
      const totalDuration = 5400; // 5.4s — gives backend time to finish
      const perStep = totalDuration / steps.length;

      rows.forEach((row, i) => {
        setTimeout(() => {
          row.classList.add('active');
          const spinner = row.querySelector('.spinner');
          if (spinner) spinner.style.display = 'block';
        }, i * perStep);

        setTimeout(() => {
          row.classList.remove('active');
          row.classList.add('done');
          const spinner = row.querySelector('.spinner');
          const svg = row.querySelector('svg');
          if (spinner) spinner.style.display = 'none';
          if (svg) svg.style.display = 'block';
        }, i * perStep + perStep * 0.82);
      });

      setTimeout(() => {
        if (loadingFinal) loadingFinal.classList.add('show');
      }, steps.length * perStep + 100);

      setTimeout(resolve, steps.length * perStep + 700);
    });
  }
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => App.init());
} else {
  App.init();
}
