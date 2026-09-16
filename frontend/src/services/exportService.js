/**
 * JobGuard AI - Export & Reporting Service
 * 
 * Provides automated forensic report formatting in Markdown, JSON,
 * and clipboard copy integrations.
 * 
 * @module services/exportService
 */

export class ExportService {
  /**
   * Generates a formal forensic markdown report from a RiskReport.
   * @param {Object} report RiskReport or history entry
   * @returns {string} Markdown formatted report
   */
  static generateMarkdown(report) {
    if (!report) return '';

    const lines = [];
    const timestamp = report.timestamp ? new Date(report.timestamp).toUTCString() : new Date().toUTCString();

    lines.push('# 🛡️ JobGuard AI - Security Forensic Report');
    lines.push(`**Generated:** ${timestamp}`);
    lines.push(`**Assessment ID:** \`${report.id || 'N/A'}\``);
    lines.push('---');
    lines.push('## 1. Job Posting Overview');
    lines.push(`- **Job Title:** ${report.jobPosting?.title || report.title || 'Untitled'}`);
    lines.push(`- **Company / Entity:** ${report.jobPosting?.company || report.company || 'Confidential'}`);
    lines.push(`- **Location:** ${report.jobPosting?.location || report.location || 'Remote'}`);
    lines.push(`- **Contact:** ${report.jobPosting?.contact || report.contact || 'N/A'}`);
    lines.push('');
    lines.push('## 2. Threat & Risk Assessment');
    lines.push(`- **Overall Risk Score:** **${report.riskScore}/100**`);
    lines.push(`- **Verdict:** **${report.riskLevel}**`);
    lines.push(`- **Heuristic Confidence:** ${report.confidence || 95}%`);
    lines.push(`- **Executive Summary:** ${report.summary || 'No summary available.'}`);
    lines.push('');
    lines.push('## 3. Detected Flags & Anomalies');

    if (report.flags && report.flags.length > 0) {
      report.flags.forEach((f, idx) => {
        lines.push(`### ${idx + 1}. [${f.severity || 'WARNING'}] ${f.title}`);
        lines.push(`- **Category:** ${f.category || 'General'}`);
        lines.push(`- **Risk Weight:** +${f.weight || 0} pts`);
        lines.push(`- **Forensic Detail:** ${f.description}`);
        lines.push('');
      });
    } else {
      lines.push('*No critical red flags or high-weight heuristics detected.*');
      lines.push('');
    }

    lines.push('## 4. Remediation & Actionable Recommendations');
    if (report.recommendations && report.recommendations.length > 0) {
      report.recommendations.forEach((rec, idx) => {
        lines.push(`${idx + 1}. ${rec}`);
      });
    } else {
      lines.push('- Proceed with standard hiring diligence.');
    }

    lines.push('');
    lines.push('---');
    lines.push('*Automated assessment provided by JobGuard AI. Built with zero-trust employment verification principles.*');

    return lines.join('\n');
  }

  /**
   * Copies text directly to the system clipboard.
   * @param {string} text 
   * @returns {Promise<boolean>}
   */
  static async copyToClipboard(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
      
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    } catch (err) {
      console.error('ExportService.copyToClipboard failed:', err);
      return false;
    }
  }

  /**
   * Triggers a browser file download for generated report text.
   * @param {string} filename 
   * @param {string} content 
   * @param {string} mimeType 
   */
  static downloadFile(filename, content, mimeType = 'text/markdown;charset=utf-8') {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}
