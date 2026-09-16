/**
 * @fileoverview Domain Entity representing an incoming Job Posting payload.
 */

export class JobPosting {
  /**
   * @param {Object} params
   * @param {string} params.rawText - The full job description/advertisement text.
   * @param {string} [params.recruiterEmail] - Optional recruiter email address.
   * @param {string} [params.jobUrl] - Optional job posting URL.
   * @param {string} [params.title] - Optional parsed/provided job title.
   * @param {string} [params.company] - Optional parsed/provided company name.
   */
  constructor({ rawText, recruiterEmail = '', jobUrl = '', title = '', company = '' }) {
    this.rawText = (rawText || '').trim();
    this.recruiterEmail = (recruiterEmail || '').trim();
    this.jobUrl = (jobUrl || '').trim();
    this.title = (title || '').trim() || this._extractFallbackTitle(this.rawText);
    this.company = (company || '').trim();
    this.createdAt = new Date().toISOString();
  }

  /**
   * Derives a clean fallback title from the first line or initial tokens of text.
   * @private
   * @param {string} text
   * @returns {string}
   */
  _extractFallbackTitle(text) {
    if (!text) return 'Untitled Job Analysis';
    const firstLine = text.split('\n')[0].replace(/[#*!]/g, '').trim();
    return firstLine.length > 60 ? firstLine.substring(0, 57) + '...' : (firstLine || 'Untitled Job Analysis');
  }

  /**
   * Validates if the payload contains sufficient information for analysis.
   * @returns {boolean}
   */
  isValid() {
    return this.rawText.length > 0 || this.recruiterEmail.length > 0 || this.jobUrl.length > 0;
  }
}
