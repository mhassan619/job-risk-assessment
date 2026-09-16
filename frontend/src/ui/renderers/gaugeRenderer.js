/**
 * JobGuard AI - Gauge & Visual Spectrum Renderer
 * 
 * Renders interactive SVG circular gauges, animated score counters,
 * and linear spectrum position indicators.
 * 
 * @module ui/renderers/gaugeRenderer
 */

import { getRiskColor } from '../../config/constants.js';

export class GaugeRenderer {
  /**
   * Updates an SVG circle gauge with animated score, color stroke, and text counter.
   * 
   * @param {number} score Score value (0 - 100)
   * @param {string} [riskLevel='medium'] Level: 'low' | 'medium' | 'high' | 'critical'
   */
  static render(score, riskLevel = 'medium') {
    const gaugeFill = document.getElementById('gaugeFill');
    const gaugeScore = document.getElementById('gaugeScore');
    const spectrumMarker = document.getElementById('spectrumMarker');

    const clampedScore = Math.max(0, Math.min(100, Math.round(score)));
    const color = getRiskColor(clampedScore);

    // SVG Circle with r=62 (circumference = 2 * PI * 62 ≈ 389.557)
    const r = 62;
    const circumference = 2 * Math.PI * r;

    if (gaugeFill) {
      gaugeFill.style.strokeDasharray = `${circumference}`;
      gaugeFill.style.strokeDashoffset = `${circumference}`;
      gaugeFill.style.stroke = color;

      requestAnimationFrame(() => {
        setTimeout(() => {
          const targetOffset = circumference - (clampedScore / 100) * circumference;
          gaugeFill.style.strokeDashoffset = `${targetOffset}`;
        }, 60);
      });
    }

    if (gaugeScore) {
      this.animateCounter(gaugeScore, clampedScore, 900);
    }

    if (spectrumMarker) {
      requestAnimationFrame(() => {
        setTimeout(() => {
          spectrumMarker.style.left = `${clampedScore}%`;
        }, 60);
      });
    }
  }

  /**
   * Smoothly animates a numeric text counter.
   * @param {HTMLElement} element 
   * @param {number} targetValue 
   * @param {number} duration 
   */
  static animateCounter(element, targetValue, duration = 900) {
    const startValue = 0;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(startValue + (targetValue - startValue) * easeOut);

      element.textContent = current;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = targetValue;
      }
    }

    requestAnimationFrame(update);
  }
}
